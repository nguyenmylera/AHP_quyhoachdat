CREATE Database Dat
Use Dat

-- 1. Bảng lưu các tiêu chí
CREATE TABLE Criteria (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);

-- 2. Bảng lưu ma trận so sánh cặp giữa các tiêu chí
CREATE TABLE CriteriaComparison (
    id INT IDENTITY(1,1) PRIMARY KEY,
    criteria_id_1 INT NOT NULL FOREIGN KEY REFERENCES Criteria(id),
    criteria_id_2 INT NOT NULL FOREIGN KEY REFERENCES Criteria(id),
    comparison_value NUMERIC(5, 2) NOT NULL
);

-- 3. Bảng lưu trọng số tiêu chí
CREATE TABLE CriteriaWeights (
    id INT IDENTITY(1,1) PRIMARY KEY,
    criteria_id INT NOT NULL FOREIGN KEY REFERENCES Criteria(id),
    weight NUMERIC(5, 4) NOT NULL
);

-- 4. Bảng lưu các phương án
CREATE TABLE Alternatives (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);
ALTER TABLE Alternatives
ALTER COLUMN name NVARCHAR(100);

-- 5. Bảng lưu điểm đánh giá phương án
CREATE TABLE AlternativeScores (
    id INT IDENTITY(1,1) PRIMARY KEY,
    alternative_id INT NOT NULL FOREIGN KEY REFERENCES Alternatives(id),
    criteria_id INT NOT NULL FOREIGN KEY REFERENCES Criteria(id),
    score NUMERIC(5, 2) NOT NULL
);
INSERT INTO Criteria (name, description) VALUES
(N'Độ cao và độ dốc địa hình', N'Đánh giá ảnh hưởng của địa hình đến việc sử dụng đất'),
(N'Nguồn nước', N'Khả năng tiếp cận và sử dụng nguồn nước'),
(N'Mật độ dân cư', N'Số lượng dân cư tại khu vực'),
(N'Diện tích đất', N'Tổng diện tích có thể khai thác'),
(N'Khoảng cách đến trung tâm', N'Khoảng cách địa lý đến trung tâm đô thị'),
(N'Cơ sở hạ tầng và dịch vụ', N'Mức độ phát triển hạ tầng và dịch vụ'),
(N'Nguồn lao động', N'Khả năng cung cấp lao động tại địa phương');

UPDATE Criteria
SET name = N'Nguồn nước'
WHERE name = N'Nguồn Nước';
-- ✅ 1. Tạo bảng Session để quản lý các phiên sử dụng
CREATE TABLE Session (
    id INT IDENTITY(1,1) PRIMARY KEY,
    created_at DATETIME DEFAULT GETDATE()
);

-- ✅ 2. Thêm cột session_id vào bảng CriteriaWeights
ALTER TABLE CriteriaWeights
ADD session_id INT NULL;

ALTER TABLE CriteriaWeights
ADD CONSTRAINT FK_CriteriaWeights_Session
FOREIGN KEY (session_id) REFERENCES Session(id);

-- ✅ 3. Thêm cột session_id vào bảng AlternativeScores
ALTER TABLE AlternativeScores
ADD session_id INT NULL;

ALTER TABLE AlternativeScores
ADD CONSTRAINT FK_AlternativeScores_Session
FOREIGN KEY (session_id) REFERENCES Session(id);


-- 1. Đổi kiểu dữ liệu sang NVARCHAR để hỗ trợ tiếng Việt
ALTER TABLE Criteria
ALTER COLUMN name NVARCHAR(255);

ALTER TABLE Criteria
ALTER COLUMN description NVARCHAR(255);

-- 2. Xóa tiêu chí trùng lặp (chỉ giữ lại tiêu chí đầu tiên)
WITH DuplicateCTE AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY name ORDER BY id) AS rn
    FROM Criteria
)
DELETE FROM DuplicateCTE WHERE rn > 1;

-- 3. Thêm ràng buộc UNIQUE để ngăn tiêu chí trùng tên
-- (Lưu ý: chỉ chạy nếu chắc chắn không còn bản trùng)
ALTER TABLE Criteria
ADD CONSTRAINT UQ_Criteria_Name UNIQUE (name);

-- 4. Xoá toàn bộ dữ liệu cũ (tuỳ chọn, nếu muốn làm sạch hoàn toàn)
-- DELETE FROM Criteria;
 --DELETE FROM Alternatives;
INSERT INTO Alternatives (name, description)
VALUES 
(N'Phát triển nông nghiệp', N'Phương án phát triển nông nghiệp bền vững'),
(N'Phát triển công nghiệp', N'Phương án phát triển khu công nghiệp và nhà máy'),
(N'Phát triển đô thị', N'Phương án mở rộng và hiện đại hóa đô thị');
ALTER TABLE Alternatives
ADD CONSTRAINT UQ_Alternative_Name UNIQUE (name);

-- Thêm cột session_id
ALTER TABLE CriteriaComparison
ADD session_id INT NULL;

-- Tạo khóa ngoại liên kết với bảng Session
ALTER TABLE CriteriaComparison
ADD CONSTRAINT FK_CriteriaComparison_Session
FOREIGN KEY (session_id) REFERENCES Session(id);

CREATE TABLE AHPAnalyses (
    analysis_id INT PRIMARY KEY IDENTITY(1,1),            -- Khóa chính, tự tăng
    session_db_id INT NOT NULL,                           -- Khóa ngoại liên kết với Session.id
    analysis_name NVARCHAR(500),                          -- Tên phân tích
    created_at DATETIME2 DEFAULT GETDATE(),               -- Thời gian tạo

    criteria_list_json NVARCHAR(MAX) NOT NULL,            -- Danh sách tiêu chí (JSON)
    alternatives_list_json NVARCHAR(MAX) NOT NULL,        -- Danh sách phương án (JSON)

    criteria_weights_json NVARCHAR(MAX),                  -- Vector trọng số tiêu chí (JSON)
    local_alternative_weights_matrix_json NVARCHAR(MAX),  -- Ma trận trọng số PA (JSON)
    final_alternative_scores_json NVARCHAR(MAX),          -- Điểm các PA (JSON)
    ranked_alternatives_json NVARCHAR(MAX),               -- Kết quả xếp hạng (JSON)

    criteria_cr FLOAT,                                    -- CR của tiêu chí
    criteria_is_consistent BIT,                           -- CR hợp lệ?
    alternative_crs_json NVARCHAR(MAX),                   -- CR các PA (JSON)

    notes NVARCHAR(MAX)        );                         -- Ghi chú

    -- ✅ Ràng buộc đúng với bảng Session bạn tạo
ALTER TABLE AHPAnalyses
ADD CONSTRAINT FK_AHPAnalyses_Session
FOREIGN KEY (session_db_id)
REFERENCES [Session](id)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- Bạn có thể thêm Index để tăng tốc độ truy vấn nếu cần, ví dụ:
CREATE INDEX IX_AHPAnalyses_SessionDbId ON AHPAnalyses(session_db_id);
CREATE INDEX IX_AHPAnalyses_CreatedAt ON AHPAnalyses(created_at DESC);

ALTER TABLE Session ADD flask_session_id NVARCHAR(255)
ALTER TABLE Session ADD CONSTRAINT UQ_Session_FlaskSessionId UNIQUE (flask_session_id)


EXEC sp_helptrigger 'dbo.AHPAnalyses';