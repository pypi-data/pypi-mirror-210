import os
import copy
import codecs
import json
from cells import Cell


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