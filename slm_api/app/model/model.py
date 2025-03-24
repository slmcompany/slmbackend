from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, Float, DateTime, Boolean,Table, MetaData
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
import json
from datetime import datetime

# Cấu hình database
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "0146424Minh"
POSTGRES_DB = "slm_app"
POSTGRES_HOST = "localhost"  # Thay đổi host thành localhost
POSTGRES_PORT = "5432"  # Cổng mặc định của PostgreSQL

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Tạo engine kết nối
engine = create_engine(DATABASE_URL, echo=True)

# Khởi tạo session
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base ORM
Base = declarative_base()

# Hàm tạo session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(16), nullable=False)
    email = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    user = relationship("User", back_populates="customers")
    pre_quotes = relationship("PreQuote", back_populates="customer")
    

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    list_users = relationship("User", back_populates="role")

class Token(Base):
    __tablename__ = 'tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    phone = Column(String(16), nullable=False, unique=True)
    last_modified = Column(DateTime, default=datetime.now, nullable=False)
    
    user = relationship("User", back_populates="tokens")

class LoginHistory(Base):
    __tablename__ = 'login_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Liên kết tới bảng User
    login_time = Column(DateTime, default=datetime.now, nullable=False)  # Thời gian đăng nhập
    ip_address = Column(String(45), nullable=True)  # Địa chỉ IP (IPv4 hoặc IPv6)
    user_agent = Column(String(255), nullable=True)  # Thông tin trình duyệt hoặc thiết bị
    created_at = Column(DateTime, default=datetime.now)  # Thời gian tạo bản ghi
    update_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # Thời gian cập nhật bản ghi

    user = relationship("User", back_populates="login_histories")  # Liên kết tới User

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Liên kết tới bảng User
    title = Column(String(255), nullable=False)  # Tiêu đề thông báo
    content = Column(Text, nullable=False)  # Nội dung thông báo
    is_read = Column(Boolean, default=False)  # Trạng thái đã đọc hay chưa
    created_at = Column(DateTime, default=datetime.now)  # Thời gian tạo thông báo

    user = relationship("User", back_populates="notifications")  # Liên kết tới User

# Thêm quan hệ ngược trong model User
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(16), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    role = relationship("Role", back_populates="list_users")
    list_customers = relationship("Customer", back_populates="user")
    login_histories = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")  # Liên kết tới LoginHistory
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")  # Liên kết tới Notification
    list_downline = relationship("User", back_populates="parent", cascade="all, delete-orphan")
    parent = relationship("User", back_populates="list_downline", remote_side=[id])
    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")
    
    customers = relationship("Customer", back_populates="user", cascade="all, delete-orphan")
    

class Sector(Base):
    __tablename__ = 'sectors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable= False)
    description = Column(Text)
    image = Column(String(300))
        
class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(16), nullable=False)
    email = Column(String(255), nullable=False)
    description = Column(Text)
    image = Column(String(300))

class Brand(Base):
    __tablename__ = 'brands'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique= True, nullable=False)
    name = Column(String(255), nullable= False)
    description = Column(Text)
    image = Column(String(300))
    


# Bảng lưu mẫu cấu trúc vật tư
class MerchandiseTemplate(Base):
    __tablename__ = 'merchandise_templates'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=False, unique=True)   # Mã loại vật tư (e.g., "OCV")
    name = Column(String(255), nullable=False, unique=True)  # Tên loại vật tư
    sector_id = Column(Integer, ForeignKey('sectors.id'), nullable=False)
    structure_json = Column(Text, nullable=False)  # Mẫu cấu trúc dạng JSON
    sector = relationship('Sector')

    def get_data_structure(self):
        """ Chuyển đổi JSON string thành dict """
        return json.loads(self.structure_json)

# Bảng vật tư được tạo từ mẫu
class Merchandise(Base):
    __tablename__ = 'merchandises'

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey('merchandise_templates.id'), nullable=False)
    brand_id = Column(Integer, ForeignKey('brands.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    code = Column(String(255), unique=True, nullable=False) # Ma code vat tu
    name = Column(String(255), nullable=False)  # Tên vật tư cụ thể
    data_sheet_link = Column(String(800), nullable=True)
    unit = Column(String(50), nullable=False)
    description_in_contract = Column(Text, nullable=False)
    data_json = Column(Text, nullable=False)  # Dữ liệu vật tư dạng JSON
    created_at = Column(DateTime, default=datetime.now)
    active = Column(Boolean, default=True)
    
    template = relationship("MerchandiseTemplate")  # Liên kết tới mẫu
    brand = relationship("Brand") # Liên kết bảng brand
    supplier = relationship("Supplier") # Liên kết bảng supplier
    price_infos = relationship("PriceInfo", back_populates="merchandise", cascade="all, delete-orphan")  # Liên kết tới PriceInfo
    images = relationship("Image", cascade="all, delete-orphan")
    pre_quote_merchandises = relationship("PreQuoteMerchandise", back_populates="merchandise", cascade="all, delete-orphan")
    
    def get_data(self):
        """ Chuyển đổi JSON string thành dict """
        return json.loads(self.data_json)

#Bảng ảnh cho vật tư
class Image(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchandise_id = Column(Integer, ForeignKey("merchandises.id"), nullable=False)
    link = Column(String(800))

class PriceInfo(Base):
    __tablename__ = 'price_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    merchandise_id = Column(Integer, ForeignKey('merchandises.id'), nullable=False)  # Foreign key to Merchandise
    import_vat = Column(Float, nullable=False)
    sale_vat = Column(Float,nullable=False)
    import_price_non_vat = Column(Float,nullable=False)
    sale_price_non_vat = Column(Float,nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    merchandise = relationship("Merchandise", back_populates="price_infos")  # Liên kết tới Merchandise

class PreQuote(Base):
    __tablename__ = 'pre_quotes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    total_price = Column(Float, nullable=False)
    installation_type = Column(String(255), nullable=False)
    kind = Column(String(255), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    status = Column(String(255), nullable=False, default='pending')
    
    customer = relationship("Customer", back_populates="pre_quotes")
    pre_quote_merchandises = relationship("PreQuoteMerchandise", cascade="all, delete-orphan", back_populates="pre_quote")

class PreQuoteMerchandise(Base):
    __tablename__ = 'pre_quote_merchandises'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pre_quote_id = Column(Integer, ForeignKey('pre_quotes.id'), nullable=False)
    merchandise_id = Column(Integer, ForeignKey('merchandises.id'), nullable=False)
    note = Column(String(500))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    merchandise = relationship("Merchandise", back_populates="pre_quote_merchandises")
    
    pre_quote = relationship("PreQuote", back_populates="pre_quote_merchandises")

if __name__ == "__main__":
    # Tạo tất cả các bảng trong cơ sở dữ liệu
    Base.metadata.create_all(bind=engine)
