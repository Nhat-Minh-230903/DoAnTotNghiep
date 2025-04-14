const fs = require('fs');
const path = require('path');

// Hàm đọc tất cả các file trong thư mục và các thư mục con
function readFilesRecursively(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    // Bỏ qua node_modules và các thư mục/file không cần thiết
    if (file === 'node_modules' || file === '.git' || file === 'dist') {
      return;
    }
    
    if (stat.isDirectory()) {
      // Nếu là thư mục, đọc đệ quy
      readFilesRecursively(filePath, fileList);
    } else {
      // Bỏ qua các file không cần thiết
      if (!file.endsWith('.log') && 
          !file.endsWith('.lock') &&
          file !== 'project-export.json') {
        try {
          const content = fs.readFileSync(filePath, 'utf8');
          fileList.push({
            path: filePath,
            content: content
          });
        } catch (err) {
          console.error(`Không thể đọc file ${filePath}:`, err);
          // Đối với file nhị phân, chỉ ghi lại đường dẫn
          fileList.push({
            path: filePath,
            content: '[Binary file]'
          });
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
