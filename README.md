# CE66-26 Code Line Chat Bot Content Management System
Repository นี้เป็นแหล่งรวม Source code ของระบบ LineCMS ซึ่งเป็นส่วนหนึ่งของวิชาโครงงาน 1 และ 2 ของกลุ่มนักศึกษาปี 4 ภาควิชาวิศวกรรมคอมพิวเตอร์ สถาบันเทคโนโลยีพระจอมเกล้าเจ้าคุณทหารลาดกระบัง ปีการศึกษา 2566  

### โครงสร้างระบบเบื้องต้น
- Backend Server -
ระบบหลังบ้านหลักของ LineCMS ทำหน้าที่รับ webhook event จาก Line Messaging API ไปประมวลผลและตอบกลับตาม event ที่เกิดขึ้น โดย source code ทั้งหมดอยู่รวมกันในโฟลเดอร์ `Backend Server`

- LIFF App -
ระบบเว็บไซต์ของ LineCMS ที่ทำงานร่วมกับ LIFF ของ Line ให้สามารถใช้งานระบบ LineCMS ได้ผ่านช่องทางเว็บไซต์ โดย source code ทั้งหมดอยู่รวมกันในโฟลเดอร์ `LIFF App`

- Model Server -
ระบบโมเดลของ LineCMS สำหรับนำรูปภาพที่ได้จากหลังบ้านมาทำการ face recognition และแบ่งกลุ่มใบหน้าโดยใช้ DBSCAN รวมถึงการสร้างกราฟความสัมพันธ์จากรูปภาพ โดย source code ทั้งหมดอยู่รวมกันในโฟลเดอร์ `Model Server`

### ส่วนเพิ่มเติม
#### Model Server
เนื่องจากโมเดลที่ใช้ใน source code มีขนาดใหญ่ไม่สามารถเพิ่มลงใน Repository นี้ได้ จึงได้เพิ่มลงในที่อื่นแทน หากต้องการใช้โมเดลเพื่อนำไปใช้งานร่วมกับ source code สามารถดาวน์โหลดได้จาดลิงค์นี้
shape_predictor_68_face_landmarks.dat: https://drive.google.com/file/d/1gcdIriP68KhQDkOu5Qj7QrhTCkHrg5Dm/view?usp=sharing
