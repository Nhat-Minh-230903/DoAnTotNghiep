# Hệ thống đánh giá môn học - Frontend

Dự án frontend cho hệ thống đánh giá môn học sử dụng React, Vite và Tailwind CSS.

## Yêu cầu hệ thống

- Node.js (phiên bản 14.0.0 trở lên)
- npm (thường được cài đặt cùng với Node.js)

## Cài đặt và chạy dự án

1. **Tải mã nguồn**

   Tải mã nguồn dự án từ repository hoặc xuất từ WebContainer.

2. **Cài đặt các dependencies**

   Mở terminal trong thư mục dự án và chạy:

   ```bash
   npm install
   ```

3. **Chạy ứng dụng trong môi trường phát triển**

   ```bash
   npm run dev
   ```

   Ứng dụng sẽ chạy tại địa chỉ [http://localhost:5173](http://localhost:5173)

## Tài khoản demo

Dự án hiện đang sử dụng dữ liệu mẫu cho việc phát triển. Bạn có thể đăng nhập với các tài khoản sau:

- **Admin**: admin@example.com / admin123
- **Giảng viên**: instructor@example.com / instructor123
- **Sinh viên**: student@example.com / student123

## Cấu trúc dự án

```
src/
├── components/       # Các component dùng chung
├── config/           # Cấu hình và hằng số
├── contexts/         # React contexts (AuthContext, etc.)
├── pages/            # Các trang của ứng dụng
│   ├── admin/        # Trang dành cho admin
│   ├── instructor/   # Trang dành cho giảng viên
│   └── student/      # Trang dành cho sinh viên
└── main.jsx          # Entry point
```

## Kết nối với Backend

Mặc định, frontend được cấu hình để kết nối với API backend tại `http://localhost:5000/api`. Bạn có thể thay đổi URL này trong file `src/config/constants.js`.

## Xây dựng cho môi trường production

Để build dự án cho môi trường production, chạy:

```bash
npm run build
```

Kết quả build sẽ được lưu trong thư mục `dist/`.
