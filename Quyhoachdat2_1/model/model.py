# model/model.py
import pyodbc
import json # Cần thiết cho việc serialize/deserialize dữ liệu JSON

# --- Cấu hình kết nối Database ---
CONN_STR = (
    r"DRIVER={SQL Server};"
    r"SERVER=MYLE\SVAD;"  # << SỬA LẠI TÊN SERVER CỦA BẠN NẾU CẦN
    r"DATABASE=Dat;"  # 
    r"Trusted_Connection=yes;"
    # r'UID=your_username;' # Bỏ comment và điền nếu dùng SQL Authentication
    # r'PWD=your_password;'
)

def get_db_connection():
    """Tạo và trả về một kết nối database SQL Server."""
    try:
        conn = pyodbc.connect(CONN_STR)
        return conn
    except pyodbc.Error as ex:
        error_message = ex.args[1] if len(ex.args) > 1 else str(ex)
        print(f"LỖI KẾT NỐI DATABASE SQL SERVER: {error_message}")
        raise

# --- Hàm CRUD cho Tiêu chí (Criteria) ---
def get_criteria_from_db():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Criteria ORDER BY id")
        criteria = [(row.id, row.name) for row in cursor.fetchall()]
        return criteria
    except pyodbc.Error as ex:
        print(f"Lỗi khi lấy tiêu chí từ DB: {ex.args[1] if len(ex.args) > 1 else str(ex)}")
        return []
    finally:
        if conn: conn.close()

def get_criteria_by_ids(criteria_ids_list):
    if not criteria_ids_list: return []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        safe_ids = [int(cid) for cid in criteria_ids_list]
        if not safe_ids: return []
        
        placeholders = ', '.join(['?'] * len(safe_ids))
        query = f"SELECT id, name FROM Criteria WHERE id IN ({placeholders}) ORDER BY id"
        cursor.execute(query, safe_ids)
        criteria = [(row.id, row.name) for row in cursor.fetchall()]
        return criteria
    except pyodbc.Error as ex:
        print(f"Lỗi khi lấy tiêu chí theo IDs: {ex.args[1] if len(ex.args) > 1 else str(ex)}")
        return []
    except ValueError as ve:
        print(f"Lỗi chuyển đổi ID tiêu chí sang integer: {ve}")
        return []
    finally:
        if conn: conn.close()

def add_criteria(name, description=""):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        db_description = description if description and description.strip() else None
        cursor.execute("INSERT INTO Criteria (name, description) VALUES (?, ?)", name, db_description)
        conn.commit()
        return True
    except pyodbc.IntegrityError: 
        print(f"Tiêu chí '{name}' đã tồn tại trong DB (vi phạm UNIQUE constraint).")
        return False
    except pyodbc.Error as ex:
        print(f"Lỗi khi thêm tiêu chí '{name}' vào DB: {ex.args[1] if len(ex.args) > 1 else str(ex)}")
        return False
    finally:
        if conn: conn.close()

# --- Hàm CRUD cho Phương án (Alternatives) ---
def get_all_alternatives():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Alternatives ORDER BY id")
        alternatives = [(row.id, row.name) for row in cursor.fetchall()]
        return alternatives
    except pyodbc.Error as ex:
        print(f"Lỗi khi lấy phương án từ DB: {ex.args[1] if len(ex.args) > 1 else str(ex)}")
        return []
    finally:
        if conn: conn.close()

def get_alternatives_by_ids(alternative_ids_list):
    if not alternative_ids_list: return []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        safe_ids = [int(aid) for aid in alternative_ids_list]
        if not safe_ids: return []

        placeholders = ', '.join(['?'] * len(safe_ids))
        query = f"SELECT id, name FROM Alternatives WHERE id IN ({placeholders}) ORDER BY id"
        cursor.execute(query, safe_ids)
        alternatives = [(row.id, row.name) for row in cursor.fetchall()]
        return alternatives
    except pyodbc.Error as ex:
        print(f"Lỗi khi lấy phương án theo IDs: {ex.args[1] if len(ex.args) > 1 else str(ex)}")
        return []
    except ValueError as ve:
        print(f"Lỗi chuyển đổi ID phương án sang integer: {ve}")
        return []
    finally:
        if conn: conn.close()

def add_alternative(name, description=""):
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        db_description = description if description and description.strip() else None
        cursor.execute("INSERT INTO Alternatives (name, description) VALUES (?, ?)", name, db_description)
        conn.commit()
        return True
    except pyodbc.IntegrityError:
        print(f"Phương án '{name}' đã tồn tại trong DB (vi phạm UNIQUE constraint).")
        return False
    except pyodbc.Error as ex:
        print(f"Lỗi khi thêm phương án '{name}' vào DB: {ex.args[1] if len(ex.args) > 1 else str(ex)}")
        return False
    finally:
        if conn: conn.close()

# --- Hàm quản lý Session ---
def get_or_create_session_db_id(flask_session_id_value):
    if not flask_session_id_value:
        print("MODEL ERROR: get_or_create_session_db_id được gọi với flask_session_id_value rỗng/None.")
        return None
    
    print(f"MODEL DEBUG: Bắt đầu get_or_create_session_db_id cho flask_session_id: {flask_session_id_value}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Kiểm tra xem flask_session_id đã tồn tại chưa
        cursor.execute("SELECT id FROM Session WHERE flask_session_id = ?", flask_session_id_value)
        row = cursor.fetchone()
        print(f"MODEL DEBUG: Tìm kiếm flask_session_id '{flask_session_id_value}', row: {row}")
        
        if row:
            session_db_id = row.id
            print(f"MODEL DEBUG: Tìm thấy session_db_id có sẵn: {session_db_id}")
            return session_db_id
        else:
            # 2. flask_session_id chưa tồn tại, tiến hành INSERT
            print(f"MODEL DEBUG: Không tìm thấy, đang tạo session DB mới cho flask_session_id: {flask_session_id_value}")
            
            # Sử dụng OUTPUT INSERTED.id
            # Câu lệnh này sẽ thực hiện INSERT và ngay lập tức trả về cột 'id' của dòng vừa được chèn.
            sql_insert_and_output_id = "INSERT INTO Session (flask_session_id) OUTPUT INSERTED.id VALUES (?);"
            
            # Thực thi câu lệnh
            cursor.execute(sql_insert_and_output_id, (flask_session_id_value,))
            
            # Lấy kết quả từ OUTPUT clause
            id_row = cursor.fetchone() 
            print(f"MODEL DEBUG: Kết quả từ OUTPUT INSERTED.id: {id_row}")
            
            if id_row and id_row[0] is not None:
                session_db_id = int(id_row[0])
                conn.commit() # Commit transaction sau khi đã lấy được ID thành công
                print(f"MODEL DEBUG: Đã tạo và commit session DB mới với ID (dùng OUTPUT): {session_db_id}")
                return session_db_id
            else:
                # Điều này không nên xảy ra nếu INSERT thành công và OUTPUT được dùng đúng cách
                print("MODEL ERROR: OUTPUT INSERTED.id không trả về ID hợp lệ sau khi INSERT vào Session. Thực hiện rollback.")
                conn.rollback() 
                return None
            
    except pyodbc.Error as ex:
        error_message = ex.args[1] if len(ex.args) > 1 else str(ex)
        print(f"MODEL ERROR: Lỗi pyodbc.Error trong get_or_create_session_db_id: {error_message}")
        if conn: conn.rollback() # Đảm bảo rollback nếu có lỗi DB
        return None
    except Exception as e: # Bắt các lỗi không mong muốn khác
        print(f"MODEL ERROR: Lỗi Exception không mong muốn trong get_or_create_session_db_id: {e}")
        if conn: conn.rollback()
        return None
    finally:
        if conn: 
            conn.close()
# --- Hàm lưu trữ các bước AHP trung gian ---
# Sử dụng session_db_id (INT) là khóa ngoại đến bảng Session(id)
# Tên cột trong DB cho khóa ngoại này là 'session_id' theo script SQL của bạn
def save_criteria_weights(session_db_id, criteria_list_with_ids, weights):
    if not all([session_db_id, criteria_list_with_ids, weights is not None]):
        print("Lỗi: Thiếu session_db_id, danh sách tiêu chí hoặc trọng số khi lưu CriteriaWeights.")
        return False
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Tên cột trong DB là 'session_id'
        cursor.execute("DELETE FROM CriteriaWeights WHERE session_id = ?", session_db_id)
        if len(criteria_list_with_ids) != len(weights):
            raise ValueError(f"Số lượng tiêu chí ({len(criteria_list_with_ids)}) và trọng số ({len(weights)}) không khớp.")
        
        for idx, (crit_id, _) in enumerate(criteria_list_with_ids):
             cursor.execute("INSERT INTO CriteriaWeights (criteria_id, weight, session_id) VALUES (?, ?, ?)",
                            crit_id, float(weights[idx]), session_db_id)
        conn.commit()
        return True
    except pyodbc.Error as ex:
        print(f"Lỗi DB khi lưu CriteriaWeights cho session_db_id {session_db_id}: {ex.args[1] if len(ex.args) > 1 else str(ex)}")
        if conn: conn.rollback()
        return False
    except ValueError as e:
         print(f"Lỗi dữ liệu khi lưu CriteriaWeights: {e}")
         if conn: conn.rollback()
         return False
    finally:
        if conn: conn.close()

def save_alternative_scores(session_db_id, alternative_list_with_ids, criteria_list_with_ids, alternative_local_weights_matrix):
    if not all([session_db_id, alternative_list_with_ids, criteria_list_with_ids, alternative_local_weights_matrix is not None]):
        print("Lỗi: Thiếu dữ liệu đầu vào khi lưu AlternativeScores.")
        return False
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Tên cột trong DB là 'session_id'
        cursor.execute("DELETE FROM AlternativeScores WHERE session_id = ?", session_db_id)
        
        rows = len(alternative_list_with_ids)
        cols = len(criteria_list_with_ids)
        
        current_shape = None
        if hasattr(alternative_local_weights_matrix, 'shape'): 
            current_shape = alternative_local_weights_matrix.shape
        elif isinstance(alternative_local_weights_matrix, list) and rows > 0 and isinstance(alternative_local_weights_matrix[0], list):
            current_shape = (len(alternative_local_weights_matrix), len(alternative_local_weights_matrix[0]))
        
        if current_shape != (rows, cols):
             raise ValueError(f"Kích thước ma trận ({current_shape}) không khớp với ({rows}, {cols}) khi lưu AlternativeScores.")

        for alt_idx in range(rows):
            alt_id = alternative_list_with_ids[alt_idx][0]
            for crit_idx in range(cols):
                crit_id = criteria_list_with_ids[crit_idx][0]
                score_value = alternative_local_weights_matrix[alt_idx][crit_idx]
                cursor.execute("INSERT INTO AlternativeScores (alternative_id, criteria_id, score, session_id) VALUES (?, ?, ?, ?)",
                               alt_id, crit_id, float(score_value), session_db_id)
        conn.commit()
        return True
    except pyodbc.Error as ex:
        print(f"Lỗi DB khi lưu AlternativeScores cho session_db_id {session_db_id}: {ex.args[1] if len(ex.args) > 1 else str(ex)}")
        if conn: conn.rollback()
        return False
    except ValueError as e:
        print(f"Lỗi dữ liệu khi lưu AlternativeScores: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()

def save_criteria_comparison_matrix(session_db_id, criteria_list_with_ids, comparison_matrix):
    if not all([session_db_id, criteria_list_with_ids, comparison_matrix is not None]):
        print("Lỗi: Thiếu dữ liệu đầu vào khi lưu CriteriaComparison.")
        return False
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Tên cột trong DB là 'session_id'
        cursor.execute("DELETE FROM CriteriaComparison WHERE session_id = ?", session_db_id)
        n_criteria = len(criteria_list_with_ids)

        current_shape = None
        if hasattr(comparison_matrix, 'shape'):
            current_shape = comparison_matrix.shape
        elif isinstance(comparison_matrix, list) and n_criteria > 0 and isinstance(comparison_matrix[0], list):
            current_shape = (len(comparison_matrix), len(comparison_matrix[0]))

        if current_shape != (n_criteria, n_criteria):
             raise ValueError(f"Kích thước ma trận ({current_shape}) không khớp với ({n_criteria}, {n_criteria}) khi lưu CriteriaComparison.")

        for i in range(n_criteria):
            crit_id_1 = criteria_list_with_ids[i][0]
            for j in range(n_criteria):
                crit_id_2 = criteria_list_with_ids[j][0]
                value = comparison_matrix[i][j]
                cursor.execute("""
                    INSERT INTO CriteriaComparison (criteria_id_1, criteria_id_2, comparison_value, session_id)
                    VALUES (?, ?, ?, ?)
                """, crit_id_1, crit_id_2, float(value), session_db_id)
        conn.commit()
        return True
    except pyodbc.Error as ex:
        print(f"Lỗi DB khi lưu CriteriaComparison cho session_db_id {session_db_id}: {ex.args[1] if len(ex.args) > 1 else str(ex)}")
        if conn: conn.rollback()
        return False
    except ValueError as e:
        print(f"Lỗi dữ liệu khi lưu CriteriaComparison: {e}")
        if conn: conn.rollback()
        return False
    finally:
        if conn: conn.close()

# --- HÀM CRUD CHO AHPAnalyses (LỊCH SỬ KẾT QUẢ CUỐI CÙNG) ---
# Sử dụng session_db_id (INT) là khóa ngoại đến bảng Session(id)


def save_ahp_analysis(session_db_id, analysis_data):
    """Lưu một kết quả phân tích AHP hoàn chỉnh vào bảng AHPAnalyses."""
    if not session_db_id:
        print("MODEL ERROR: session_db_id không hợp lệ khi gọi save_ahp_analysis.")
        return None
    
    print(f"MODEL DEBUG: Bắt đầu save_ahp_analysis cho session_db_id: {session_db_id}")
    conn = None
    analysis_id = None 
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql_params = (
            session_db_id,
            analysis_data.get('analysis_name'), 
            json.dumps(analysis_data.get('criteria_names', [])),
            json.dumps(analysis_data.get('alternatives', [])),
            json.dumps(analysis_data.get('criteria_weights', [])),
            json.dumps(analysis_data.get('local_alternative_weights_matrix', [])),
            json.dumps(analysis_data.get('alternative_scores', [])),
            json.dumps(analysis_data.get('ranked_alternatives', [])),
            analysis_data.get('cr_criteria'), 
            1 if analysis_data.get('is_consistent_criteria') else 0, 
            json.dumps(analysis_data.get('alternative_crs', {})),
            analysis_data.get('notes') 
        )

        # Sử dụng OUTPUT INSERTED.analysis_id
        # Tên cột identity của bạn trong bảng AHPAnalyses là 'analysis_id'
        sql_insert_with_output = """
            INSERT INTO AHPAnalyses (
                session_db_id, analysis_name, 
                criteria_list_json, alternatives_list_json,
                criteria_weights_json, local_alternative_weights_matrix_json,
                final_alternative_scores_json, ranked_alternatives_json,
                criteria_cr, criteria_is_consistent, alternative_crs_json, notes
            ) 
            OUTPUT INSERTED.analysis_id -- Lấy giá trị của cột analysis_id vừa được chèn
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); 
        """
        
        cursor.execute(sql_insert_with_output, sql_params)
        print("MODEL DEBUG: Đã thực hiện INSERT vào AHPAnalyses với OUTPUT clause.")
        
        analysis_id_row = cursor.fetchone() # Lấy kết quả từ OUTPUT clause
        print(f"MODEL DEBUG: Kết quả từ OUTPUT INSERTED.analysis_id: {analysis_id_row}")

        if analysis_id_row and analysis_id_row[0] is not None:
            analysis_id = int(analysis_id_row[0])
            conn.commit()
            print(f"MODEL SUCCESS: Đã lưu AHPAnalysis với ID: {analysis_id} cho session_db_id: {session_db_id}")
            return analysis_id 
        else:
            # Điều này rất lạ nếu INSERT thành công nhưng OUTPUT không trả về gì
            print("MODEL ERROR: OUTPUT INSERTED.analysis_id không trả về ID hợp lệ. Thực hiện rollback.")
            conn.rollback()
            return None

    except pyodbc.Error as ex:
        error_message = ex.args[1] if len(ex.args) > 1 else str(ex)
        print(f"MODEL ERROR (pyodbc): Lỗi khi lưu AHPAnalysis (ID có thể là {analysis_id}): {error_message}")
        if conn: conn.rollback()
        return None
    except Exception as e: 
        print(f"MODEL ERROR (Exception): Lỗi không mong muốn khi lưu AHPAnalysis (ID có thể là {analysis_id}): {e}")
        if conn: conn.rollback()
        return None
    finally:
        if conn: 
            conn.close()

# ... (các hàm khác giữ nguyên) ...

def get_ahp_analyses_by_session_db_id(session_db_id):
    """Lấy danh sách tóm tắt các phân tích AHP cho một session_db_id."""
    if not session_db_id: return []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Tên cột trong AHPAnalyses là session_db_id
        cursor.execute("""
            SELECT analysis_id, session_db_id, analysis_name, created_at 
            FROM AHPAnalyses 
            WHERE session_db_id = ? 
            ORDER BY created_at DESC
        """, (session_db_id,))
        columns = [column[0] for column in cursor.description]
        analyses = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return analyses
    except pyodbc.Error as ex:
        print(f"Lỗi DB khi lấy danh sách AHP Analyses: {ex.args[1] if len(ex.args) > 1 else str(ex)}")
        return []
    finally:
        if conn: conn.close()

def get_ahp_analysis_by_id(analysis_id, session_db_id_check=None):
    """
    Lấy chi tiết một phân tích AHP dựa trên analysis_id.
    Có thể kiểm tra session_db_id_check để đảm bảo quyền sở hữu.
    """
    if not analysis_id: return None
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql_query = "SELECT * FROM AHPAnalyses WHERE analysis_id = ?"
        params = [analysis_id]
        
        if session_db_id_check is not None: 
            # Tên cột trong AHPAnalyses là session_db_id
            sql_query += " AND session_db_id = ?"
            params.append(session_db_id_check)
            
        cursor.execute(sql_query, tuple(params))
        
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        
        if row:
            analysis_data = dict(zip(columns, row))
            
            try:
                analysis_data['criteria_names'] = json.loads(analysis_data.get('criteria_list_json', '[]'))
                analysis_data['alternatives'] = json.loads(analysis_data.get('alternatives_list_json', '[]'))
                analysis_data['criteria_weights'] = json.loads(analysis_data.get('criteria_weights_json', 'null'))
                analysis_data['local_alternative_weights_matrix'] = json.loads(analysis_data.get('local_alternative_weights_matrix_json', 'null'))
                analysis_data['alternative_scores'] = json.loads(analysis_data.get('final_alternative_scores_json', 'null'))
                analysis_data['ranked_alternatives'] = json.loads(analysis_data.get('ranked_alternatives_json', 'null'))
                analysis_data['alternative_crs'] = json.loads(analysis_data.get('alternative_crs_json', '{}')) 
            except json.JSONDecodeError as je:
                print(f"Lỗi JSON decode cho analysis_id {analysis_id}: {je}. Dữ liệu JSON có thể không hợp lệ.")
                # Gán giá trị mặc định nếu parse lỗi để tránh lỗi khi render template
                default_if_json_error = lambda key: [] if 'list' in key or 'names' in key or 'alternatives' in key and 'scores' not in key else ({} if 'crs' in key else None)
                for k in ['criteria_list_json', 'alternatives_list_json', 'criteria_weights_json', 'local_alternative_weights_matrix_json', 'final_alternative_scores_json', 'ranked_alternatives_json', 'alternative_crs_json']:
                    key_parsed = k.replace('_json','').replace('final_','').replace('list_','').replace('local_','')
                    if key_parsed == "alternatives_list": key_parsed = "alternatives" # Sửa tên cho khớp
                    if key_parsed == "alternative_scores": key_parsed = "alternative_scores"
                    if key_parsed == "ranked_alternatives": key_parsed = "ranked_alternatives"

                    if not isinstance(analysis_data.get(key_parsed), (list, dict, float, int, type(None))): # Nếu chưa parse thành công
                         analysis_data[key_parsed] = default_if_json_error(k)

            analysis_data['is_consistent_criteria'] = bool(analysis_data.get('criteria_is_consistent'))
            
            keys_to_delete = [k for k in analysis_data if k.endswith('_json')]
            keys_to_delete.append('criteria_is_consistent') 
            for k in keys_to_delete:
                if k in analysis_data:
                    del analysis_data[k]
            return analysis_data
        return None
    except pyodbc.Error as ex:
        print(f"Lỗi DB khi lấy chi tiết AHP Analysis ID {analysis_id}: {ex.args[1] if len(ex.args) > 1 else str(ex)}")
        return None
    finally:
        if conn: conn.close()

# Không cần chạy init_db() từ đây nữa nếu DB đã được tạo bằng script SQL riêng.
# if __name__ == '__main__':
#     print("Thực thi init_db() để đảm bảo các bảng tồn tại (chỉ chạy khi cần thiết lập DB)...")
#     init_db()
