# Báo cáo Day 6: [ĐIỀN tên đề tài ngắn]

> Thay **mọi** ô có chữ ĐIỀN nằm trong ngoặc vuông bằng nội dung của bạn, xoá luôn cả dấu ngoặc vuông. Lệnh `python tools/check_submission.py` sẽ báo FAIL nếu còn sót bất kỳ chỗ nào.

- **Họ tên:** Nguyễn Thành Nam
- **MSSV:** 2A202602827 
- **Lớp:** K4-L3-Track4
- **Link repo:** https://github.com/Danniel-Jame/NguyenThanhNam-2A202602827-Track4-Day21/tree/main
- **Topic:** A — LiDAR-camera projection QA
- **Dataset:**data/kitti_mini
- **Các frame đã dùng:** frame 000011

> Hãy viết ngắn: mỗi mục từ 3 đến 8 dòng, ưu tiên số liệu và hình ảnh.

## 1. Claim

Một câu khẳng định kỹ thuật có thể kiểm chứng. Ví dụ: *"Lệch yaw 1° làm 12% điểm LiDAR rơi ra khỏi vật thể ở 30 m, phát hiện được bằng edge-alignment score với ngưỡng X."*

[ĐIỀN]

## 2. Evidence

Bảng hoặc plot số liệu, kèm ảnh/video demo. Ghi rõ đường dẫn file trong `results/`.

| Cấu hình / mức perturb | Metric 1 | Metric 2 | Ghi chú |
|---|---|---|---|
| [ĐIỀN] | | | |

![demo](../results/figures/[ĐIỀN].png)

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

Use-case cụ thể (ADAS / robot / drone), trade-off và bước tiếp theo.

[ĐIỀN]

## 5. Cách chạy lại

Các lệnh tái tạo lại toàn bộ kết quả từ repo sạch.

```bash
[ĐIỀN]
```

## 6. Khai báo sử dụng AI

Ghi rõ đã dùng công cụ AI nào, dùng vào việc gì, và bạn đã tự kiểm chứng kết quả đó bằng cách nào. Nếu không dùng AI, ghi "Không sử dụng". Xem quy định ở `RULES.md` mục 2.

| Công cụ | Dùng cho việc gì | Bạn đã kiểm chứng thế nào |
|---|---|---|
| [ĐIỀN] | | |
