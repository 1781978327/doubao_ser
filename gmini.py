# setup
import google.generativeai as genai
 
 
genai.configure(api_key='AIzaSyBp1EGZxIBODHYql53nE1gchZ3TQpyqg08')  # 填入自己的api_key
 
# 查询模型
for m in genai.list_models():
    print(m.name)
    print(m.supported_generation_methods)