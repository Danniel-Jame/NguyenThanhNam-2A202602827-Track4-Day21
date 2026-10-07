# Báo cáo Day 6: Đánh giá ảnh hưởng của lệch góc Yaw trong LiDAR-Camera Projection

- **Họ tên:** Nguyễn Thành Nam
- **MSSV:** 2A202602827
- **Lớp:** K4-L3-Track4
- **Link repo:** https://github.com/Danniel-Jame/NguyenThanhNam-2A202602827-Track4-Day21/tree/main
- **Topic:** A — LiDAR-camera projection QA
- **Dataset:** data/kitti_mini
- **Các frame đã dùng:** frame 000011

## 1. Claim

Khi giả lập nhiễu góc yaw từ $0.0^\circ$ đến $5.0^\circ$ trên frame `000011` (KITTI Mini), phần trăm điểm LiDAR chiếu vào ảnh biến động nhẹ từ $18.42\%$ đến $18.48\%$, nhưng số điểm rơi vào trong các 2D bounding boxes tăng từ $2079$ lên $2273$ điểm ($+9.33\%$) do toàn bộ dải điểm LiDAR bị trôi ngang sang bên phải, dẫn đến điểm từ nền và vật thể khác bị dịch chuyển đè vào khung nhãn 2D.

## 2. Evidence

Dưới đây là số liệu chi tiết thu được từ thí nghiệm sweep góc yaw perturb trên frame `000011` với seed=42:

| Cấu hình / mức perturb | Điểm trong ảnh | % Trong ảnh | Điểm trong 2D BBox | Depth trung bình (m) | Ghi chú |
|---|---|---|---|---|---|
| Yaw 0.0° (Baseline) | 19,946 | 18.47% | 2,079 | 16.79 | Chuẩn calibration gốc |
| Yaw 0.5° | 19,946 | 18.47% | 2,098 | 16.82 | Lệch nhẹ sang phải |
| Yaw 1.0° | 19,952 | 18.47% | 2,123 | 16.85 | Bắt đầu trôi khỏi mép đối tượng |
| Yaw 1.5° | 19,950 | 18.47% | 2,170 | 16.88 | Điểm từ nền đè vào 2D BBox |
| Yaw 2.0° | 19,963 | 18.48% | 2,204 | 16.90 | Điểm LiDAR lệch rõ rệt khỏi vật thể |
| Yaw 3.0° | 19,948 | 18.47% | 2,239 | 16.95 | Biến dạng hình học lớn |
| Yaw 5.0° | 19,897 | 18.42% | 2,273 | 17.00 | Sai lệch hoàn toàn |

![Biểu đồ Yaw Perturbation Sweep](/results/figures/yaw_perturb_sweep_plot.png)

- File CSV dữ liệu chi tiết: `results/yaw_perturb_sweep.csv`
- File biểu đồ minh họa: `results/figures/yaw_perturb_sweep_plot.png`

## 3. Phân tích Failure Case & Debugging

    ### 3.1. Hình ảnh minh họa lỗi
    - **Tên file ảnh:** `results/figures/fail_01_yaw_2deg_pole.png`
    - **Frame bị lỗi:** `000011` (Dataset KITTI Mini)
    - **Điều kiện thử nghiệm:** Lệch góc Yaw `+2.0°` (Simulated Yaw Drift)

    ### 3.2. Mô tả hiện tượng và Nguyên nhân
    - **Mô tả hiện tượng:** 
    Khi thực hiện phép chiếu Point Cloud lên ảnh camera với thông số ma trận ngoại (Extrinsic) bị lệch góc Yaw 2.0°, toàn bộ các điểm LiDAR trên xe hơi và biển báo/cột điện phía xa bị lệch ngang (theo phương x của ảnh) sang bên phải so với vị trí thực tế trên ảnh 2D.
    - **Tác động:** 
    Các điểm LiDAR đại diện cho chiếc xe hơi ở khoảng cách ~15m-20m rơi hoàn toàn ra khỏi khung 2D Bounding Box của nhãn (Label Box). Một số điểm LiDAR của mặt đường bị chiếu lên phía trên thân xe.

    ### 3.3. Xếp loại lớp lỗi (Debug Class)
    - **Lớp debug:** **Geometry (Hình học / Hệ tọa độ)**
    - **Giải thích xếp loại:** 
    Lỗi xuất phát từ việc ma trận biến đổi không gian $T_{velo\_to\_cam}$ bị sai lệch thông số góc xoay (Extrinsic Calibration Errors). Dữ liệu I/O đọc đúng, thời gian đồng bộ chuẩn, nhưng phép biến đổi hình học từ không gian 3D LiDAR sang không gian 3D Camera bị sai lệch góc dẫn đến sai tọa độ sau khi chiếu pixel.

    ### 3.4. Đề xuất giải pháp khắc phục trên hệ thống thực tế
    1. **Online Recalibration:** Triển khai thuật toán tự động căn chỉnh ma trận ngoại (Automatic Extrinsic Calibration) dựa trên các đặc trưng hình học (cột điện, vạch kẻ đường, mép đường) giữa điểm LiDAR và ảnh Camera khi xe đang chạy.
    2. **Monitoring & Alert:** Thiết lập chỉ số đo độ trùng khớp (dựa trên mật độ điểm rơi vào trong 2D box của các đối tượng đã biết) để cảnh báo hệ thống tạm ngắt chế độ tự hành khi phát hiện Calibration Drift vượt quá ngưỡng an toàn ($>0.5^\circ$).

## 4. Khuyến nghị nếu triển khai thật

Trong hệ thống ADAS/Robot tự hành thực tế, hiện tượng lệch calibration góc xoay yaw làm suy giảm nghiêm trọng độ tin cậy của mô hình sensor fusion. Để đảm bảo vận hành an toàn:
- **Trade-off:** Giữa tần suất kiểm tra calibration tự động và chi phí tính toán trên xe. Cần cân bằng việc lọc điểm nhiễu thời gian thực mà không làm tăng đáng kể latency của pipeline nhận dạng.
- **Bước tiếp theo:** Tích hợp bộ lọc Kalmann hoặc khung Online Recalibration liên tục theo dõi độ biến động của mép điểm LiDAR so với cạnh đối tượng 2D trong ảnh thu được từ camera.

## 5. Cách chạy lại

    Các lệnh tái tạo lại toàn bộ kết quả từ repo sạch:

    ```bash
    # 1. Chạy thử phép chiếu chuẩn baseline và tạo ảnh failure case
    python -m starter.projection --data-root data/kitti_mini --frame 000011 --yaw-deg 2.0

    # 2. Chạy script thí nghiệm chính sweep yaw perturb (tạo CSV và biểu đồ)
    python src/run_experiments.py

    # 3. Kiểm tra tính đầy đủ trước khi nộp
    python tools/check_submission.py

## 6. Khai báo sử dụng AI

Ghi rõ đã dùng công cụ AI nào, dùng vào việc gì, và bạn đã tự kiểm chứng kết quả đó bằng cách nào. Nếu không dùng AI, ghi "Không sử dụng". Xem quy định ở `RULES.md` mục 2.


| Công cụ | Dùng cho việc gì | Bạn đã kiểm chứng thế nào |
| :--- | :--- | :--- |
| Gemini / ChatGPT | Hỗ trợ tổng hợp báo cáo và viết script vẽ biểu đồ | Đã tự đối chiếu trực tiếp dữ liệu từ file `yaw_perturb_sweep.csv` và kiểm tra hình ảnh xuất ra bằng file script `tools/check_submission.py` |

