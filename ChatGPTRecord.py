import json
import datetime
import os

class ChatGPTRecord:
    def __init__(self, objective):
        self.data = []
        self.id = 0
        self.objective = objective

        # 取得當前日期
        date = datetime.date.today().strftime("%Y%m%d")
        # ensure record folder
        record_folder = "./chatGPT_record/"
        if not os.path.exists(record_folder):
            os.makedirs(record_folder)

        # 檢查是否有重複的檔案名稱，並計算出新的檔名
        i = 1
        while os.path.exists(os.path.join(record_folder, f"{date}-{self.objective}-{i}")):
            i += 1
        
        self.filepath = os.path.join(record_folder, f"{date}-{self.objective}-{i}")
        os.makedirs(self.filepath)
        self.filename = os.path.join(self.filepath, f"{self.objective}.json")

    def add_record(self, prompt_content, chatGPT_response):
        record = {"id": self.id, "prompt": prompt_content, "chatGPT": chatGPT_response}
        self.data.append(record)
        self.id += 1
        with open(self.filename, "w", encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False)
    
    def convert_to_text(self):
        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        filename = os.path.splitext(self.filename)[0]  # 移除副檔名
        base_filename = os.path.basename(filename)  # 取得檔名
        directory = os.path.join(os.path.dirname(filename), base_filename)  # 取得目錄路徑
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        for record in data:
            record_id = record["id"]
            txt_filename = f"{base_filename}-{record_id}.txt"
            txt_filepath = os.path.join(directory, txt_filename)
            
            with open(txt_filepath, "w", encoding="utf-8") as txt_file:
                txt_file.write(f"id:{record_id}\n\nprompt:\n{record['prompt']}\n\nchatGPT:\n{record['chatGPT']}\n")

if __name__ == '__main__':
    #ChatGPTRecord.convert_to_text("20230613-訂火車票-6.json")
    record = ChatGPTRecord("測試")
    print(record.filename)
    record.add_record("test","test")
    record.convert_to_text()