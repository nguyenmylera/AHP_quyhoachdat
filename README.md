# Hệ thống Hỗ trợ Ra quyết định Quy hoạch và Phân bổ Đất đai (AHP)

Ứng dụng web Flask này được xây dựng để hỗ trợ quá trình ra quyết định sử dụng Phương pháp Phân tích Thứ bậc (AHP). Nó cho phép người dùng định nghĩa các tiêu chí và phương án, thực hiện so sánh cặp theo thang đo Saaty, tính toán trọng số, kiểm tra tính nhất quán, và cuối cùng là đưa ra xếp hạng cho các phương án. Hệ thống cũng hỗ trợ lưu trữ lịch sử các phân tích (liên kết với phiên làm việc của người dùng) và xuất kết quả ra file Excel và PDF.

## Mục lục

- [Yêu cầu Hệ thống](#yêu-cầu-hệ-thống)
- [Hướng dẫn Cài đặt](#hướng-dẫn-cài-đặt)
  - [Bước 1: Tải Mã nguồn và Chuẩn bị Môi trường](#bước-1-tải-mã-nguồn-và-chuẩn-bị-môi-trường)
  - [Bước 2: Cài đặt các Thư viện Python](#bước-2-cài-đặt-các-thư-viện-python)
  - [Bước 3: Chuẩn bị Font chữ cho Xuất PDF](#bước-3-chuẩn-bị-font-chữ-cho-xuất-pdf)
  - [Bước 4: Thiết lập Cơ sở dữ liệu SQL Server bằng file .sql](#bước-4-thiết-lập-cơ-sở-dữ-liệu-sql-server-bằng-file-sql)
  - [Bước 5: Cấu hình Chuỗi Kết nối Cơ sở dữ liệu](#bước-5-cấu-hình-chuỗi-kết-nối-cơ-sở-dữ-liệu)
  - [Bước 6: Chạy Ứng dụng](#bước-6-chạy-ứng-dụng)
- [Hướng dẫn Sử dụng](#hướng-dẫn-sử-dụng)
## Yêu cầu Hệ thống

- **Python:** Phiên bản 3.7 trở lên (khuyến nghị 3.9+).
- **PIP:** Trình quản lý gói của Python (thường đi kèm với Python).
- **SQL Server:** Hệ quản trị cơ sở dữ liệu.
- **SQL Server Management Studio (SSMS)** hoặc một công cụ tương tự để thực thi file SQL.
- **Trình duyệt Web:** Một trình duyệt hiện đại như Chrome, Firefox, Edge, hoặc Safari.
- **Driver ODBC cho SQL Server:** Cần thiết để `pyodbc` có thể kết nối đến SQL Server. (Thường đã có sẵn trên Windows hoặc có thể tải từ Microsoft).

## Hướng dẫn Cài đặt

### Bước 1: Tải Mã nguồn và Chuẩn bị Môi trường

1.  **Clone kho chứa từ GitHub:**
    Mở terminal hoặc Git Bash và chạy lệnh sau:
    ```bash
    git clone https://github.com/nguyenmylera/AHP_quyhoachdat.git
    ```
2.  **Di chuyển vào thư mục dự án:**
    ```bash
    cd Quyhoachdat2_1
    ```
3.  **Tạo Môi trường ảo (Khuyến nghị):**
    ```bash
    python -m venv venv
    ```
4.  **Kích hoạt Môi trường ảo:**
    *   Trên Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   Trên macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    Sau khi kích hoạt, bạn sẽ thấy `(venv)` ở đầu dòng lệnh của mình.

### Bước 2: Cài đặt các Thư viện Python

Đảm bảo bạn đã kích hoạt môi trường ảo. Trong thư mục gốc của dự án, nếu có file `requirements.txt`, hãy chạy:
```bash
pip install -r requirements.txt
```
### Bước 3: Chuẩn bị Font chữ cho Xuất PDF
 *  Chức năng xuất PDF yêu cầu font chữ hỗ trợ tiếng Việt. Tải file font DejaVuSans.ttf từ địa chỉ: https://www.1001fonts.com/dejavu-sans-font.html (Hoặc từ nguồn DejaVu Fonts trên GitHub để có bản chuẩn).
 *  Trong thư mục dự án của bạn, tạo thư mục theo đường dẫn: static/fonts/ (nếu chưa có).
 *  Sao chép file DejaVuSans.ttf vừa tải về vào thư mục static/fonts/.
### Bước 4: Thiết lập Cơ sở dữ liệu SQL Server bằng file .sql
 *  Mở SQL Server Management Studio (SSMS).Kết nối đến SQL Server Instance của bạn.
 *  Mở một cửa sổ "New Query" trong SSMS.Mở file dat.sql bằng một trình soạn thảo văn bản, sao chép toàn bộ nội dung của nó.
 *  Dán nội dung đã sao chép vào cửa sổ "New Query" trong SSMS.
 *  Nhấn nút "Execute" (hoặc phím F5) để chạy script.
 *  Kiểm tra cửa sổ "Messages" trong SSMS để đảm bảo không có lỗi nào xảy ra trong quá trình thực thi. Các bảng (Sessions, Criteria, Alternatives, AHPAnalyses, v.v.) sẽ được tạo trong database Dat.
### Bước 5: Cấu hình Chuỗi Kết nối Cơ sở dữ liệu
 *  Mở file model/model.py trong dự án của bạn.
 *  Tìm đến biến CONN_STR ở đầu file.
 *  Đảm bảo chuỗi kết nối khớp với cấu hình SQL Server và tên database của bạn (thường là Dat nếu bạn làm theo Bước 4):
![alt text](https://github.com/user-attachments/assets/822c4cc8-e2c7-481e-8798-cf51d28ea468)
### Bước 6: Chạy ứng dụng Flask
``` bash
python app.py
```
## Hướng dẫn Sử dụng
### 1.Trang chủ (/):
 *  Thêm các Tiêu chí và Phương án mới nếu cơ sở dữ liệu của bạn chưa có sẵn.
 *  Chọn các Tiêu chí (ít nhất 4) và Phương án (ít nhất 3) bạn muốn sử dụng cho phân tích AHP.
 *  Nhấn "Bắt đầu AHP & Tính Ma trận Tiêu chí".
### 2.So sánh Tiêu chí (Bước 1):
 *  Điền giá trị so sánh cặp giữa các tiêu chí theo thang đo Saaty (1-9 hoặc 1/n, ví dụ 1/2, 1/3,...,1/9).
 *  Nhấn "Tính Trọng số Tiêu chí & Chuyển bước".
 *  Xem kết quả trọng số và CR của ma trận tiêu chí. Nếu không nhất quán (CR > 0.1), bạn sẽ được yêu cầu sửa lại và các thông số sẽ không được lưu.
### 3.So sánh Phương án (Bước 2):
* Nếu ma trận tiêu chí nhất quán, các form so sánh cặp phương án theo từng tiêu chí sẽ hiện ra.
* Điền giá trị so sánh cho từng ma trận theo thang đo Saaty.
* Nhấn "Tính Điểm Cuối cùng & Xem Kết quả".
* Hệ thống sẽ hiển thị chi tiết AHP (bao gồm WSV, CV, CR, v.v.) cho từng ma trận phương án con. Nếu có ma trận nào không nhất quán (CR > 0.1) hoặc có lỗi nhập liệu, bạn sẽ được yêu cầu sửa lại trước khi xem kết quả cuối cùng; việc tính toán sẽ không tiếp tục cho đến khi tất cả các ma trận phương án đều hợp lệ và nhất quán.
### 4.Trang Kết quả:
* Hiển thị chi tiết phân tích, các bảng trọng số (trọng số cục bộ của phương án theo tiêu chí, trọng số tiêu chí), điểm số tổng hợp, xếp hạng các phương án, và biểu đồ trực quan hóa.
* Cho phép xuất kết quả ra file Excel và PDF.
* Kết quả phân tích sẽ được tự động lưu vào lịch sử của phiên làm việc hiện tại trong cơ sở dữ liệu.
### 5.Lịch sử Phân tích:
* Truy cập mục này từ sidebar để xem lại các lần phân tích AHP đã được lưu vào cơ sở dữ liệu, liên kết với phiên làm việc của bạn.
