import os
import copy
import codecs
import json


# 코드 입력 문구 (코드를 삭제하고 출력을 박제하는 Cell)
code_input_msgs = [
    '# 코드입력',
    '# 코드를 입력하세요.',
    '# 코드를 입력해 주세요',
]

# 검증코드 (출력 값을 삭제하지 않음)
validation_msgs =  [
    '# 검증코드',
    '# 코드 검증',
    '# 코드검증',
]

option_msgs = {
    'code': code_input_msgs, 
    'validation': validation_msgs,
}

css_table_align_left = [
    'div.output_area .rendered_html table {\n',
    '   margin-left: 0;\n',
    '   margin-right: 0;\n',
    '}\n'
]

fixed_code_input_text = '# ▼ 코드를 입력해 주세요 ▼ #'

class Cell():
    def __init__(self, json_obj, option_msgs=option_msgs, remain_code=False, add_solution=False, use_fixed_code_input_text=True, clear_cell_output=True):
        """
        json_obj: ipynb json Object
        option_msgs: # 코드입력, # 코드검증과 같은 메시지
        remain_code: # 코드입력 Cell 의 코드 삭제 여부. True: 유지, False: 삭제. 기본값: False
        add_solution: 정답지 출력을 마크다운 셀로 추가 생성
        use_fixed_code_input_text: 고정된 코드를 입력해 주세요 문구 출력 여부. True: 고정 문구 출력, False: 첫 문장을 문구로 출력
        clear_cell_output: 모든 셀의 출력 값을 Clear 여부. 기본값: True(초기화)        
        """
        self.json_obj = json_obj
        
        # cell_type: 'code' or 'markdown'
        self.cell_type = json_obj['cell_type']
        
        # 코드입력 / 검증코드 문구
        self.option_msgs = option_msgs
        
        # input_type: None, 'code', 'validation'
        self.input_type = None
        
        # 코드입력 Cell 의 코드 삭제 여부
        self.remain_code = remain_code
        
        # 출력(output) 존재 여부
        self.outputs = None
        
        # 정답 코드
        self.answer_code = None
        
        # 정답지 표기 여부
        self.add_solution = add_solution
        
        # 코드를 입력해 주세요 고정 문구 활용 여부
        self.use_fixed_code_input_text = use_fixed_code_input_text
        
        # 일반 Cell의 출력 초기화
        self.clear_cell_output = clear_cell_output
        
        # 초기화 진행
        self.initialize()
        
    def initialize(self):
        if 'execution_count' in self.json_obj:
            self.json_obj['execution_count'] = None
        
        msg_idx = 0
        
        # Source 코드가 존재하는 경우
        if 'source' in self.json_obj:
            for i, source in enumerate(self.json_obj['source']):
                for msg in self.option_msgs['code']:
                    if msg in source:
                        self.input_type = 'code'
                        msg_idx = i
                        break
                    
                for msg in self.option_msgs['validation']:
                    if msg in source:
                        self.input_type = 'validation'
                        break
                    
        # 코드 입력창 초기화 처리
        if self.input_type == 'validation' and 'outputs' in self.json_obj:
            pass
        
        elif self.input_type == 'code' and 'source' in self.json_obj:
            # '코드입력' or '코드를 입력해 주세요' 문구 등의 처리
            code_input_header = self.json_obj['source'][msg_idx]
            
            # 정답을 추가하여 출력 생성하는 경우
            if self.add_solution:
                answer_code = copy.deepcopy(self.json_obj['source'])
                answer_code.pop(msg_idx)
                self.answer_code = answer_code
                    
            
            if self.remain_code == False:
                self.json_obj['source'].clear()
                
                if self.use_fixed_code_input_text:
                    self.json_obj['source'].append(fixed_code_input_text)
                else:
                    self.json_obj['source'].append(code_input_header)
                self.json_obj['source'].append('\n')
            else:
                if self.use_fixed_code_input_text:
                    self.json_obj['source'][0] = fixed_code_input_text + '\n'
            
        elif 'outputs' in self.json_obj and self.clear_cell_output:
            self.json_obj['outputs'].clear()
            
        # 출력창 처리
        if self.input_type == 'code' and 'outputs' in self.json_obj and len(self.json_obj['outputs']) > 0:
            if 'data' in self.json_obj['outputs'][0]:
                # Series, DataFrame 출력
                # data = self.json_obj['outputs'][0]['data']
                for output_ in self.json_obj['outputs']:
                    data = output_['data']
                    if 'text/html' in data:
                        # DataFrame 출력
                        html = data['text/html']
                        html.insert(0, '<p><strong>[출력 결과]</strong></p>')
                        replaced_html = []
                        for row in html:
                            row = row.replace(r'<div>', r'<div class="output_subarea output_html rendered_html output_result">')
                            row = row.replace(r'class="dataframe"', r'class="dataframe" style="margin-left: 0; margin-right: 0;"')
                            replaced_html.append(row)
                        
                        self.outputs = replaced_html
                        # break
                        
                    elif 'text/plain' in data:
                        # print('test/plain FOUND!!')
                        # Plain TEXT 출력
                        plain_text = data['text/plain']
                        if len(plain_text) > 0 and plain_text[0].startswith('<Figure'):
                            self.outputs = None
                            # continue
                        else:
                            plain_text[0] = '<pre>' + plain_text[0]
                            plain_text[len(plain_text)-1] = plain_text[len(plain_text)-1] + '</pre>'
                            plain_text.insert(0, '<p><strong>[출력 결과]</strong></p>')
                            self.outputs = plain_text
                            
                    if 'image/png' in data:
                        # print('IMAGE FOUND!!')
                        # pyplot 그래프
                        plain_image = data['image/png']
                        plain_image = '<img style="margin-left: 0; margin-right: 0;" src="data:image/png;base64,' + plain_image.replace('\n','') + '"/>'
                        self.outputs = []
                        self.outputs.insert(0, '<p><strong>[출력 결과]</strong></p>')
                        self.outputs.append(plain_image)
                        break
                    
            elif 'text' in self.json_obj['outputs'][0]:
                # Series 형태의 TEXT output
                text = self.json_obj['outputs'][0]['text']
                if len(text) > 0 and text[0].startswith('<Figure'):
                    self.outputs = None
                else:
                    text[0] = '<pre>' + text[0]
                    text[len(text)-1] = text[len(text)-1] + '</pre>'
                    text.insert(0, '<p><strong>[출력 결과]</strong></p>')
                    self.outputs = text
    
    def create_answer_output(self):
        if self.answer_code is not None:
            answer_output = [
                '<details>\n',
                '<summary>\n',
                '<b>▼ [정답 확인] ▼</b>\n',
                '</summary>\n',
                '<div class="markdown">\n',
                '<span><pre><code>',
                # import pandas as pd

            # pd.read_csv('data.csv')
                
            ]
            answer_output.extend(self.answer_code)
            answer_output.append('\n</code></pre></span></div></details>\n',)
            return answer_output
        else:
            return None
        
    def get_type(self):
        return self.cell_type
    
    def get_input_type(self):
        return self.input_type
    
    def get(self, tag):
        if tag in self.json_obj:
            return self.json_obj[tag]
        else:
            return None
        
    def set(self, tag, value):
        if tag in self.json_obj:
            self.json_obj[tag] = value
            return True
        else:
            return False
        
    def keys(self):
        return self.json_obj.keys()
    
    def __call__(self):
        return self.json_obj


def convert_notebook(src_file, tgt_file=None, post_fix='-(변환).ipynb', folder_path='실습', remain_code=False, add_solution=False):
    if add_solution:
        post_fix = post_fix[:-6] + '-(정답추가)' + '.ipynb'
        
    if remain_code:
        post_fix = post_fix[:-6] + '-(코드유지)' + '.ipynb'
        
    try:
        f = codecs.open(src_file, 'r')
        source = f.read()
    except UnicodeDecodeError:
        f = codecs.open(src_file, 'r', encoding='utf-8')
        source = f.read()
    except Exception as e:
        raise Exception("파일 변환에 실패 했습니다. 에러 메세지:" + e)

    # json 로드
    y = json.loads(source)

    # Cell 복사
    y_cells = copy.deepcopy(y['cells'])

    # Cell 생성
    cells = [Cell(c, remain_code=remain_code, add_solution=add_solution) for c in y_cells]

    # 최종 출력 셀들의 집합
    processed_cells = []

    for i, cell in enumerate(cells):        
        if cell.input_type == 'code':    
            if cell.outputs is None:
                # 출력 값이 없는 코드셀인 경우
                processed_cells.append(cell())
            else:
                # 출력결과가 존재하는 경우 (DataFrame, Series, 그래프 등)
                if len(cell.outputs) > 0:
                    output_cell = {'cell_type': 'markdown', 
                                'metadata': {},
                                'source': cell.outputs}
                    c = copy.deepcopy(cell())
                    if 'outputs' in c:
                        c['outputs'] = []
                    processed_cells.append(c)
                    processed_cells.append(output_cell)
                    
            if cell.answer_code is not None:
                # 정답 출력이 존재하는 경우 (추가 Cell 생성)
                answer_output = cell.create_answer_output()    
                if answer_output is not None:
                    answer_output_cell = {'cell_type': 'markdown', 
                            'metadata': {},
                            'source': answer_output}
                    processed_cells.append(answer_output_cell)
        elif cell.input_type == 'markdown':
            # 출력 값이 없는 코드셀인 경우
            processed_cells.append(cell())  
        else:
            processed_cells.append(cell())  
            
    y['cells'] = processed_cells

    if tgt_file is None:
        if '해설' in source:
            tgt_file = src_file.replace('해설', '실습')
            tgt_file = tgt_file[:-6] + post_fix
        else:
            tgt_file = src_file[:-6] + post_fix
        
    # 파일이름 저장 (메타데이터에 적용)
    title = tgt_file.split('.')[0]
    title = title.split('/')[-1]

    if folder_path is not None:
        # 폴더 경로 없으면 생성
        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)
        # 폴더 경로를 포함한 파일 경로 생성
        output_filename = os.path.join(folder_path, os.path.basename(tgt_file))

    # 메타데이터
    colab = y['metadata'].get('colab')
    if colab:
        y['metadata']['colab']['name'] = title

    with open(output_filename, "w") as json_file:
        json.dump(y, json_file)
    print('생성완료')
    print(f'파일명: {output_filename}')