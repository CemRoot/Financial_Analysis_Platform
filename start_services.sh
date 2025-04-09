#!/bin/bash

# Financial Analysis Platform başlatma betiği
echo "Financial Analysis Platform başlatılıyor..."

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Çalışma dizinine geç
cd "$(dirname "$0")"

# PostgreSQL veritabanını kontrol et
echo -e "${YELLOW}PostgreSQL veritabanı durumu kontrol ediliyor...${NC}"
if ! pg_isready -q; then
    echo "PostgreSQL veritabanı çalışmıyor. Lütfen başlatın."
    echo "MacOS: brew services start postgresql"
    echo "Linux: sudo service postgresql start"
    echo "Windows: PostgreSQL servisini başlatın"
    exit 1
fi
echo -e "${GREEN}PostgreSQL veritabanı çalışıyor.${NC}"

# Backend için sanal ortamı aktif et (yoksa oluştur)
if [ ! -d "./backend/venv" ]; then
    echo -e "${YELLOW}Backend için sanal ortam oluşturuluyor...${NC}"
    python3 -m venv ./backend/venv
    echo -e "${GREEN}Sanal ortam oluşturuldu.${NC}"
fi

# Backend bağımlılıklarını kur
echo -e "${YELLOW}Backend bağımlılıkları kuruluyor...${NC}"
source ./backend/venv/bin/activate
pip install -r ./backend/requirements.txt
echo -e "${GREEN}Backend bağımlılıkları kuruldu.${NC}"

# Veritabanı migrasyonlarını yap
echo -e "${YELLOW}Veritabanı migrasyonları yapılıyor...${NC}"
cd backend
python manage.py makemigrations
python manage.py migrate
echo -e "${GREEN}Veritabanı migrasyonları tamamlandı.${NC}"

# Superuser oluşturma kontrolü
echo -e "${YELLOW}Admin kullanıcısı kontrol ediliyor...${NC}"
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Admin kullanıcısı var' if User.objects.filter(username='admin').exists() else 'Admin kullanıcısı yok')"

read -p "Admin kullanıcısı oluşturmak ister misiniz? (E/h): " CREATE_ADMIN
if [[ $CREATE_ADMIN =~ ^[Ee]$ || $CREATE_ADMIN == "" ]]; then
    echo "Admin kullanıcısı oluşturuluyor..."
    python manage.py createsuperuser --username admin --email admin@example.com
fi

# Backend'i başlat
echo -e "${YELLOW}Backend başlatılıyor...${NC}"
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!
echo -e "${GREEN}Backend başlatıldı (PID: $BACKEND_PID).${NC}"

# Backend çalışma dizininden çık
cd ..

# Frontend için Node modüllerini kur
echo -e "${YELLOW}Frontend bağımlılıkları kuruluyor...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
echo -e "${GREEN}Frontend bağımlılıkları kuruldu.${NC}"

# Frontend'i başlat
echo -e "${YELLOW}Frontend başlatılıyor...${NC}"
npm start &
FRONTEND_PID=$!
echo -e "${GREEN}Frontend başlatıldı (PID: $FRONTEND_PID).${NC}"

# Bilgi mesajı göster
echo ""
echo -e "${GREEN}Financial Analysis Platform başlatıldı:${NC}"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo "- Admin Panel: http://localhost:8000/admin"
echo ""
echo "Çıkmak için CTRL+C tuşuna basın."

# CTRL+C yakalandığında çalışacak fonksiyon
trap ctrl_c INT
function ctrl_c() {
    echo ""
    echo -e "${YELLOW}Servisler durduruluyor...${NC}"
    kill $BACKEND_PID
    kill $FRONTEND_PID
    echo -e "${GREEN}Servisler durduruldu.${NC}"
    exit 0
}

# Servislerin çalışmasını bekle
wait