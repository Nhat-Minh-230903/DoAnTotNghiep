# Hướng dẫn xuất dự án từ WebContainer

Để tải dự án từ WebContainer về máy tính của bạn, bạn có thể thực hiện theo các bước sau:

## Phương pháp 1: Tải từng file

1. Mở từng file trong WebContainer
2. Sao chép nội dung của file
3. Tạo file tương ứng trên máy tính của bạn và dán nội dung vào

## Phương pháp 2: Sử dụng tính năng Export của WebContainer (nếu có)

Một số môi trường WebContainer có tính năng Export hoặc Download, cho phép bạn tải toàn bộ dự án dưới dạng file ZIP.

## Phương pháp 3: Tạo script để xuất dự án

Bạn có thể tạo một script để in ra nội dung của tất cả các file trong dự án, sau đó sao chép và lưu vào máy tính của bạn.

```javascript
// Lưu file này với tên export-project.js
const fs = require('fs');
const path = require('path');

// Hàm đọc tất cả các file trong thư mục và các thư mục con
function readFilesRecursively(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      // Nếu là thư mục, đọc đệ quy
      readFilesRecursively(filePath, fileList);
    } else {
      // Bỏ qua các file không cần thiết
      if (file !== 'node_modules' && 
          file !== '.git' && 
          !file.endsWith('.log') &&
          !file.endsWith('.lock')) {
        try {
          const content = fs.readFileSync(filePath, 'utf8');
          fileList.push({
            path: filePath,
            content: content
          });
        } catch (err) {
          console.error(`Không thể đọc file ${filePath}:`, err);
        }
      }
    }
  });
  
  return fileList;
}

// Đọc tất cả các file trong dự án
const projectFiles = readFilesRecursively('.');

// In ra thông tin về các file
console.log(JSON.stringify(projectFiles, null, 2));
```

Chạy script này với lệnh:

```bash
node export-project.js > project-export.json
```

Sau đó, bạn có thể tải file `project-export.json` về máy tính và sử dụng nó để tạo lại cấu trúc dự án.

## Sau khi tải về

Sau khi đã tải dự án về máy tính, hãy làm theo các hướng dẫn trong file README.md để cài đặt và chạy dự án.
