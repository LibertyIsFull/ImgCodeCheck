import ddddocr
import base64

# 测试ddddocr 1.5.6的API使用方式
def test_ddddocr_api():
    # 直接测试创建实例和分类方法
    print("Testing ddddocr API...")
    
    try:
        # 创建实例
        ocr = ddddocr.DdddOcr()
        print("✓ Successfully created DdddOcr instance")
        
        # 测试方法存在性
        if hasattr(ocr, 'classification'):
            print("✓ classification method exists")
        else:
            print("✗ classification method not found")
            
        # 检查是否有其他识别方法
        print(f"Available methods: {[method for method in dir(ocr) if not method.startswith('_')]}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ddddocr_api()