@echo off
title Silver Tracker Dashboard Server
echo ==============================================
echo       KHOI DONG SILVER TRACKER DASHBOARD
echo ==============================================
echo.

:: Check if python is available in PATH
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [LOI CRITICAL] Khong tim thay lenh 'python' tren he thong cua ban!
    echo.
    echo Nguyen nhan: 
    echo 1. Ban chua cai dat Python:
    echo    Vui long tai va cai dat tu https://www.python.org/ (Phien ban 3.8 tro len)
    echo 2. Ban da cai dat nhung chua tich o "Add python.exe to PATH" khi cai dat:
    echo    Vui long mo lai file cai dat Python, chon "Modify" hoac go di cai lai,
    echo    va NHO TICH VAO o "Add python.exe to PATH".
    echo.
    echo ----------------------------------------------------
    echo GOI Y FALLBACK (Offline):
    echo Ban van co the xem bieu do va gia quoc te bang cach double-click truc tiep
    echo vao file 'index.html' trong thu muc nay (nhung se khong cap nhat live gia Phu Quy).
    echo ----------------------------------------------------
    echo.
    pause
    exit /b
)

echo May chu dang duoc khoi dong tai cong 8085...
echo Trinh duyet se tu dong mo trang http://127.0.0.1:8085 sau giay lat.
echo.
echo Luu y: Giu nguyen cua so nay de duy tri ket noi cap nhat gia.
echo.

:: Start browser
start "" "http://127.0.0.1:8085"

:: Run the python server
python app.py
if %errorlevel% neq 0 (
    echo.
    echo [LOI] May chu gap su co trong khi dang chay.
    echo Vui long kiem tra cac dong thong bao loi phia tren.
    echo.
    pause
)
