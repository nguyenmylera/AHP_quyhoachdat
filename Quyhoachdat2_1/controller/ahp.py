# controller/ahp.py
import numpy as np
import math

RI_lookup = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
    11: 1.51,
    12: 1.54,
    13: 1.56,
    14: 1.57,
    15: 1.59,
}


def parse_saaty_value(value_str, is_diagonal=False):
    value_str = (
        str(value_str).strip().replace(",", ".")
    )  # Đảm bảo xử lý dấu phẩy thập phân

    if is_diagonal:
        if value_str == "1":
            return 1.0
        raise ValueError("Giá trị trên đường chéo chính phải là 1.")

    # Ưu tiên xử lý dạng phân số "1/n" trước
    if "/" in value_str:
        parts = value_str.split("/")
        if len(parts) == 2 and parts[0].strip() == "1":
            try:
                denominator = int(parts[1].strip())
                if 2 <= denominator <= 9:
                    return 1.0 / denominator
                else:
                    raise ValueError("Mẫu số của phân số 1/n phải từ 2 đến 9.")
            except ValueError:  # Lỗi này có thể xảy ra nếu parts[1] không phải là số
                raise ValueError(
                    f"Định dạng phân số không hợp lệ: {value_str}. Chỉ chấp nhận 1/n với n từ 2-9."
                )
        else:
            raise ValueError(
                f"Định dạng phân số không hợp lệ: {value_str}. Chỉ chấp nhận 1/n."
            )

    # Xử lý số
    try:
        val = float(value_str)  # Thử chuyển đổi sang float trước
    except ValueError:
        raise ValueError(
            f"Giá trị không hợp lệ: '{value_str}'. Phải là số nguyên (1-9) hoặc phân số (1/2-1/9)."
        )

    # Kiểm tra số nguyên
    if val.is_integer():  # Kiểm tra xem float có phải là số nguyên không
        val_int = int(val)
        if 1 <= val_int <= 9:
            return float(val_int)  # Trả về float để nhất quán
        else:
            # Nếu là số nguyên nhưng không nằm trong khoảng 1-9
            # Kiểm tra xem có phải là giá trị nghịch đảo hợp lệ không (ví dụ 0.25, 0.5, ...)
            # Đây là phần mở rộng để chấp nhận float từ Excel
            # Danh sách các giá trị nghịch đảo Saaty hợp lệ (làm tròn để so sánh float)
            valid_saaty_reciprocals = {round(1 / d, 10) for d in range(2, 10)}
            if round(val, 10) in valid_saaty_reciprocals:
                return val  # Chấp nhận float này nếu nó là một nghịch đảo Saaty
            raise ValueError(
                f"Số nguyên '{value_str}' không hợp lệ. Chỉ được phép là từ 1 đến 9, hoặc giá trị thập phân tương đương phân số Saaty (ví dụ 0.25, 0.5)."
            )
    else:
        # Nếu là số thập phân (không phải số nguyên)
        # Kiểm tra xem có phải là giá trị nghịch đảo hợp lệ không
        valid_saaty_reciprocals = {round(1 / d, 10) for d in range(2, 10)}
        if round(val, 10) in valid_saaty_reciprocals:
            return val  # Chấp nhận float này
        else:
            raise ValueError(
                f"Giá trị thập phân '{value_str}' không tương ứng với thang đo Saaty. Phải là số nguyên (1-9) hoặc phân số (1/2-1/9 hoặc giá trị thập phân tương đương như 0.25, 0.5)."
            )


def calculate_ahp(matrix_input, matrix_name_for_error="Ma trận"):
    # Khởi tạo results với các key mà template matrix.html và result.html mong đợi
    results = {
        "n": 0,
        "weights": None,
        "wsv": None,
        "cv": None,
        "lambdaMax": None,
        "ci": None,
        "RI": None,
        "CR": None,  # Key cho matrix.html
        "is_consistent": False,
        "error": None,
        "colSums": None,
        "normMatrix": None,  # Tùy chọn
    }
    n_val_for_except = 0
    try:
        matrix = (
            np.array(matrix_input, dtype=float)
            if not isinstance(matrix_input, np.ndarray)
            else matrix_input.astype(float)
        )
        n = matrix.shape[0]
        n_val_for_except = n
        results["n"] = n
        if n == 0 or matrix.shape[1] != n:
            raise ValueError("Ma trận không hợp lệ hoặc không vuông.")
        if np.isnan(matrix).any() or np.isinf(matrix).any():
            raise ValueError("Ma trận chứa giá trị không hợp lệ (NaN/Infinity).")

        tolerance = 1e-9
        for i in range(n):
            if not math.isclose(matrix[i, i], 1.0, abs_tol=tolerance):
                raise ValueError(
                    f"Giá trị trên đường chéo tại [{i+1},{i+1}] ({matrix[i,i]:.3f}) phải bằng 1."
                )
        # Không print warning đối xứng nữa

        col_sums_np = matrix.sum(axis=0)
        results["colSums"] = col_sums_np.tolist()  # Trả về list

        if np.any(col_sums_np <= tolerance):
            problem_cols = [
                idx + 1 for idx, s_val in enumerate(col_sums_np) if s_val <= tolerance
            ]
            raise ValueError(
                f"Các cột trong ma trận ({matrix_name_for_error}) có tổng gần bằng 0: cột {problem_cols}."
            )

        norm_matrix_np = np.divide(
            matrix,
            col_sums_np[np.newaxis, :],
            out=np.zeros_like(matrix),
            where=col_sums_np[np.newaxis, :] != 0,
        )
        results["normMatrix"] = norm_matrix_np.tolist()  # Trả về list

        weights_np = norm_matrix_np.mean(axis=1)
        weights_sum = weights_np.sum()
        if weights_sum > tolerance:
            weights_np = weights_np / weights_sum
        else:
            weights_np = np.ones(n) / n
        results["weights"] = weights_np.tolist()  # Trả về list

        weighted_sum_vector_np = np.dot(matrix, weights_np)
        results["wsv"] = weighted_sum_vector_np.tolist()  # **** ĐẢM BẢO KEY 'wsv' ****

        consistency_vector_calculated_np = np.zeros_like(weights_np)
        non_zero_weights_indices = np.abs(weights_np) > tolerance

        if np.any(np.isnan(weighted_sum_vector_np)) or np.any(
            np.isinf(weighted_sum_vector_np)
        ):
            raise ValueError(
                f"Vector tổng trọng số (WSV) của {matrix_name_for_error} chứa NaN/Infinity."
            )

        if np.any(non_zero_weights_indices):
            safe_weights = weights_np[non_zero_weights_indices]
            safe_wsv = weighted_sum_vector_np[non_zero_weights_indices]
            consistency_vector_calculated_np[non_zero_weights_indices] = np.divide(
                safe_wsv,
                safe_weights,
                out=np.full_like(safe_wsv, float(n)),
                where=np.abs(safe_weights) > tolerance * 1e-3,
            )

        if np.any(np.isnan(consistency_vector_calculated_np)) or np.any(
            np.isinf(consistency_vector_calculated_np)
        ):
            consistency_vector_calculated_np[
                np.isnan(consistency_vector_calculated_np)
                | np.isinf(consistency_vector_calculated_np)
            ] = float(n)

        results["cv"] = (
            consistency_vector_calculated_np.tolist()
        )  # **** ĐẢM BẢO KEY 'cv' ****
        # Bỏ key 'consistency_vector' nếu không dùng để tránh nhầm lẫn

        valid_cv_elements = consistency_vector_calculated_np[
            non_zero_weights_indices
            & ~np.isnan(consistency_vector_calculated_np)
            & ~np.isinf(consistency_vector_calculated_np)
        ]
        lambda_max_val = (
            valid_cv_elements.mean() if len(valid_cv_elements) > 0 else float(n)
        )
        results["lambdaMax"] = float(lambda_max_val)  # Key cho template matrix.html

        ci_val = (lambda_max_val - n) / (n - 1) if n > 1 else 0.0
        results["ci"] = float(ci_val)  # Key cho template matrix.html

        ri_val = RI_lookup.get(n, 1.59)
        ri_val = 0.0 if n <= 2 else ri_val
        results["RI"] = float(ri_val)  # Key cho template matrix.html (đã là RI)

        cr_val = (
            ci_val / ri_val
            if ri_val > tolerance
            else (0.0 if math.isclose(ci_val, 0.0, abs_tol=tolerance) else float("inf"))
        )
        results["CR"] = float(cr_val)  # Key cho template matrix.html (đã là CR)

        results["is_consistent"] = bool(
            cr_val <= 0.1 + tolerance
        )  # Key cho template matrix.html

        return results

    except ValueError as ve:
        error_msg = f"Lỗi dữ liệu AHP ({matrix_name_for_error}): {ve}"
        print(error_msg)
        final_error_results = {k: None for k in results.keys()}
        final_error_results.update(
            {"n": n_val_for_except, "error": error_msg, "is_consistent": False}
        )
        return final_error_results
    except Exception as e:
        error_msg = f"Lỗi không xác định trong AHP ({matrix_name_for_error}): {type(e).__name__} - {e}"
        print(error_msg)
        final_error_results = {k: None for k in results.keys()}
        final_error_results.update(
            {"n": n_val_for_except, "error": error_msg, "is_consistent": False}
        )
        return final_error_results


def get_sorted_criteria_with_weights(criteria_results, db_criteria_tuples):
    sorted_list = []
    if criteria_results and criteria_results.get("weights") and db_criteria_tuples:
        try:
            if len(criteria_results["weights"]) == len(db_criteria_tuples):
                criteria_with_weights_and_names = list(
                    zip(criteria_results["weights"], db_criteria_tuples)
                )
                sorted_list = sorted(
                    criteria_with_weights_and_names,
                    key=lambda item: item[0],
                    reverse=True,
                )
        except TypeError:
            pass
    return sorted_list
