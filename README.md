# Financial Analysis Platform

<p align="center">
  <img src="docs/images/logo.png" alt="Financial Analysis Platform Logo" width="200"/>
</p>

[English](#english) | [Türkçe](#turkish)

<a name="english"></a>
## English

The Financial Analysis Platform is a comprehensive web application designed for financial analysis, stock tracking, news aggregation, and AI-powered predictions. This platform provides users with real-time data and insights to make informed investment decisions.

### Features

- **Real-Time Stock Data**: Track stocks with detailed information and interactive charts
- **Financial News**: Access the latest financial news and perform sentiment analysis on articles
- **ML-Powered Predictions**: Utilize machine learning algorithms for stock predictions and sentiment analysis
- **News-Based Stock Forecasting**: Analyze news sentiment and its correlation with stock prices to make more accurate predictions using Facebook Prophet
- **Customizable Dashboard**: Personalize your dashboard with widgets tailored to your preferences
- **Watchlists**: Manage and track your favorite stocks easily
- **User Authentication**: Secure user accounts with JWT-based authentication
- **Responsive Design**: Fully responsive web application for desktop and mobile devices

### Architecture

The application follows a modern client-server architecture:

- **Backend**: RESTful API built with Django and Django REST Framework
- **Frontend**: Single-page application built with React
- **Database**: PostgreSQL for robust data storage
- **Authentication**: JWT-based authentication for secure access
- **Containerization**: Docker support for easy deployment

### Technology Stack

#### Backend:
- **Django 4.2**: A high-level Python web framework
- **Django REST Framework**: Toolkit for building Web APIs
- **PostgreSQL**: Advanced open-source relational database
- **JWT Authentication**: Secure user authentication
- **TensorFlow & scikit-learn**: ML libraries for predictive analytics
- **Facebook Prophet**: For time series forecasting
- **News API Integration**: Real-time financial news with sentiment analysis

#### Frontend:
- **React 18**: JavaScript library for building user interfaces
- **Material UI**: React UI framework for responsive layouts
- **Chart.js & Recharts**: Libraries for interactive charts
- **Redux**: For state management
- **React Router**: For navigation
- **Axios**: For API requests

### Installation

#### Prerequisites:
- **Python 3.9+**
- **Node.js 16+**
- **PostgreSQL 13+**
- **Docker** (optional, for containerized deployment)

#### Environment Setup:
Before running the application, you need to set up environment variables:

1. Create a `.env` file in the `backend` directory with the following variables:
```
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
NEWS_API_KEY=your_news_api_key
GOOGLE_CLOUD_PROJECT=your_google_cloud_project
GOOGLE_APPLICATION_CREDENTIALS=path_to_google_credentials
```

#### One-Command Installation:
To set up the application, run the following command:

```bash
./start_services.sh
```

#### Manual Installation:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Financial_Analysis_Platform.git
   cd Financial_Analysis_Platform
   ```

2. **Set up the backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

3. **Set up the frontend**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Usage

- Access the application at `http://localhost:3000` for the frontend
- Access the API at `http://localhost:8002/api/`
- Use the admin interface at `http://localhost:8002/admin/`

### Project Structure

```
Financial_Analysis_Platform/
├── backend/                # Django backend
│   ├── apps/               # Application modules
│   │   ├── accounts/       # User authentication and profiles
│   │   ├── dashboard/      # Dashboard views and widgets
│   │   ├── news/           # News aggregation and sentiment
│   │   ├── predictions/    # ML models and predictions
│   │   └── stocks/         # Stock data and analysis
│   ├── financial_analysis/ # Project settings
│   ├── manage.py           # Django management script
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── public/             # Static files
│   ├── src/                # Source code
│   │   ├── components/     # Reusable components
│   │   ├── contexts/       # React contexts
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── styles/         # CSS and styling
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Docker configuration
└── start_services.sh       # Setup script
```

### API Documentation

The API documentation is available at `http://localhost:8002/api/swagger/` when running the development server.

### Testing

To run the test suite:

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

### Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

### License

This project is licensed under the BSD License. See the [LICENSE](LICENSE) file for more details.

---

<a name="turkish"></a>
## Türkçe

Finansal Analiz Platformu, finansal analiz, hisse senedi takibi, haber toplama ve yapay zeka destekli tahminler için tasarlanmış kapsamlı bir web uygulamasıdır. Bu platform, kullanıcılara bilinçli yatırım kararları almak için gerçek zamanlı veriler ve içgörüler sağlar.

### Özellikler

- **Gerçek Zamanlı Hisse Senedi Verileri**: Detaylı bilgiler ve interaktif grafiklerle hisse senetlerini takip edin
- **Finansal Haberler**: En son finansal haberlere erişin ve makaleler üzerinde duygu analizi yapın
- **ML Destekli Tahminler**: Hisse senedi tahminleri ve duygu analizi için makine öğrenimi algoritmalarını kullanın
- **Haber Tabanlı Hisse Senedi Tahmini**: Facebook Prophet kullanarak haber duyarlılığını ve hisse senedi fiyatlarıyla ilişkisini analiz ederek daha doğru tahminler yapın
- **Özelleştirilebilir Gösterge Paneli**: Tercihlerinize göre uyarlanmış widget'larla gösterge panelinizi kişiselleştirin
- **İzleme Listeleri**: Favori hisse senetlerinizi kolayca yönetin ve takip edin
- **Kullanıcı Kimlik Doğrulama**: JWT tabanlı kimlik doğrulama ile güvenli kullanıcı hesapları
- **Duyarlı Tasarım**: Masaüstü ve mobil cihazlar için tamamen duyarlı web uygulaması

### Mimari

Uygulama, modern bir istemci-sunucu mimarisini takip eder:

- **Backend**: Django ve Django REST Framework ile oluşturulmuş RESTful API
- **Frontend**: React ile oluşturulmuş tek sayfalık uygulama
- **Veritabanı**: Sağlam veri depolama için PostgreSQL
- **Kimlik Doğrulama**: Güvenli erişim için JWT tabanlı kimlik doğrulama
- **Konteynerleştirme**: Kolay dağıtım için Docker desteği

### Teknoloji Yığını

#### Backend:
- **Django 4.2**: Yüksek seviyeli bir Python web çerçevesi
- **Django REST Framework**: Web API'leri oluşturmak için araç seti
- **PostgreSQL**: Gelişmiş açık kaynaklı ilişkisel veritabanı
- **JWT Kimlik Doğrulama**: Güvenli kullanıcı kimlik doğrulaması
- **TensorFlow ve scikit-learn**: Tahmine dayalı analitik için ML kütüphaneleri
- **Facebook Prophet**: Zaman serisi tahmini için
- **Haber API Entegrasyonu**: Duygu analizi ile gerçek zamanlı finansal haberler

#### Frontend:
- **React 18**: Kullanıcı arayüzleri oluşturmak için JavaScript kütüphanesi
- **Material UI**: Duyarlı düzenler için React UI çerçevesi
- **Chart.js ve Recharts**: İnteraktif grafikler için kütüphaneler
- **Redux**: Durum yönetimi için
- **React Router**: Gezinme için
- **Axios**: API istekleri için

### Kurulum

#### Ön Koşullar:
- **Python 3.9+**
- **Node.js 16+**
- **PostgreSQL 13+**
- **Docker** (isteğe bağlı, konteynerli dağıtım için)

#### Ortam Kurulumu:
Uygulamayı çalıştırmadan önce, ortam değişkenlerini ayarlamanız gerekir:

1. `backend` dizininde aşağıdaki değişkenlerle bir `.env` dosyası oluşturun:
```
SECRET_KEY=django_gizli_anahtariniz
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=veritabani_adiniz
DB_USER=veritabani_kullanici_adiniz
DB_PASSWORD=veritabani_sifreniz
DB_HOST=localhost
DB_PORT=5432
NEWS_API_KEY=haber_api_anahtariniz
GOOGLE_CLOUD_PROJECT=google_cloud_projeniz
GOOGLE_APPLICATION_CREDENTIALS=google_kimlik_bilgilerinizin_yolu
```

#### Tek Komutla Kurulum:
Uygulamayı kurmak için aşağıdaki komutu çalıştırın:

```bash
./start_services.sh
```

#### Manuel Kurulum:

1. **Depoyu klonlayın**:
   ```bash
   git clone https://github.com/yourusername/Financial_Analysis_Platform.git
   cd Financial_Analysis_Platform
   ```

2. **Backend'i kurun**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows'ta: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

3. **Frontend'i kurun**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

### Kullanım

- Frontend için uygulamaya `http://localhost:3000` adresinden erişin
- API'ye `http://localhost:8002/api/` adresinden erişin
- Admin arayüzüne `http://localhost:8002/admin/` adresinden erişin

### Proje Yapısı

```
Financial_Analysis_Platform/
├── backend/                # Django backend
│   ├── apps/               # Uygulama modülleri
│   │   ├── accounts/       # Kullanıcı kimlik doğrulama ve profiller
│   │   ├── dashboard/      # Gösterge paneli görünümleri ve widget'lar
│   │   ├── news/           # Haber toplama ve duygu analizi
│   │   ├── predictions/    # ML modelleri ve tahminler
│   │   └── stocks/         # Hisse senedi verileri ve analizi
│   ├── financial_analysis/ # Proje ayarları
│   ├── manage.py           # Django yönetim betiği
│   └── requirements.txt    # Python bağımlılıkları
├── frontend/               # React frontend
│   ├── public/             # Statik dosyalar
│   ├── src/                # Kaynak kodu
│   │   ├── components/     # Yeniden kullanılabilir bileşenler
│   │   ├── contexts/       # React bağlamları
│   │   ├── pages/          # Sayfa bileşenleri
│   │   ├── services/       # API servisleri
│   │   └── styles/         # CSS ve stil
│   └── package.json        # Node.js bağımlılıkları
├── docker-compose.yml      # Docker yapılandırması
└── start_services.sh       # Kurulum betiği
```

### API Belgeleri

API belgeleri, geliştirme sunucusunu çalıştırırken `http://localhost:8002/api/swagger/` adresinde mevcuttur.

### Test

Test paketini çalıştırmak için:

```bash
# Backend testleri
cd backend
python manage.py test

# Frontend testleri
cd frontend
npm test
```

### Katkıda Bulunma

Katkılar memnuniyetle karşılanır! Herhangi bir geliştirme veya hata düzeltmesi için lütfen bir pull request göndermekten veya bir sorun açmaktan çekinmeyin.

1. Depoyu forklayın
2. Bir özellik dalı oluşturun: `git checkout -b feature/ozellik-adiniz`
3. Değişikliklerinizi commit edin: `git commit -m 'Bazı özellikler ekle'`
4. Dalınıza push yapın: `git push origin feature/ozellik-adiniz`
5. Bir pull request gönderin

### Lisans

Bu proje BSD Lisansı altında lisanslanmıştır. Daha fazla ayrıntı için [LICENSE](LICENSE) dosyasına bakın.