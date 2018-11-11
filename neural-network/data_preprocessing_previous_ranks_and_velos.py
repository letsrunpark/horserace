# coding: utf-8

import pandas as pd
import numpy as np


## 전처리

'''
#### race_noheader

1. race_noheader 에서 "distance" 가져오기 (속력을 구하기 위해)

2. primary key는 "date" & "round" (아래의 race_result table 과 merge 할 예정
'''
race_db = pd.read_csv('/Users/daham/Downloads/tables 181110/race_noheader.csv').drop_duplicates()
first_row_race_db = np.array(race_db.columns)
tmp_race_db = np.array(race_db)

final_race_df = pd.DataFrame(np.vstack((first_row_race_db, tmp_race_db)))
final_race_df = final_race_df[[0, 1, 5]]
final_race_df.columns = ['date', 'round', 'distance']

# 날짜별 라운드별 Distance 만 있는 데이터프레임을 출력함



'''
#### to_sql_race_result

1. to_sql_race_result 에서 데이터 모두 가져오기

2. primary key는 "date" & "round" 로 해서 위에서 구한 final_race_df 와 merge

3. "distance" / "record" 로 속도를 계산

4. 이전 3경기의 순위를 새로운 컬럼에 기록 

5. 이전 3경기의 속도를 새로운 컬럼에 기록
'''

# 1. to_sql_race_result 에서 데이터 모두 가져오기
to_sql_race_result_df = pd.read_csv('/Users/daham/Downloads/tables 181110/to_sql_race_result.csv').drop_duplicates()
first_row_rae_result = np.array(to_sql_race_result_df.columns)
tmp_to_sql_race_result_df = np.array(to_sql_race_result_df)

final_to_sql_race_result_df = pd.DataFrame(np.vstack((first_row_rae_result, tmp_to_sql_race_result_df)),
                                           columns=['url', 'date', 'round', 'name', 'code', 'rank', 'lane', 'sex',
                                                    'age', 'jockey_w', 'rating', 'jockey', 'difference', 'weight',
                                                    'dandivi', 'yeondivi', 'equipment', 's1fr', 'c1r', 'c2r', 'c3r',
                                                    'c4r', 'g1fr', 's1f', 'c1', 'c2', 'c3', 'c4', 'g3f', 'record'])

# 2. primary key는 "date" & "round" 로 해서 위에서 구한 final_race_df 와 merge
merged_df_with_race_info_and_race_result = final_to_sql_race_result_df.merge(final_race_df, how='left',
                                                                             on=['date', 'round'])

# 3. "distance" / "record" 로 속도를 계산
merged_df_with_race_info_and_race_result['velocity'] = merged_df_with_race_info_and_race_result['distance'] / \
                                                       merged_df_with_race_info_and_race_result['record']


# 말 종류별 리스트를 먼저 출력
horse_list = list(merged_df_with_race_info_and_race_result.name.unique())

empty_list = []

# 4. 이전 3경기의 순위를 새로운 컬럼에 기록
# 5. 이전 3경기의 속도를 새로운 컬럼에 기록
for i in horse_list:
    tmp = merged_df_with_race_info_and_race_result.loc[
        merged_df_with_race_info_and_race_result.name == i, ['date', 'name', 'rank', 'velocity']].sort_values('date',

                                                                                                              ascending=False)
    tmp['prev1_rank'] = tmp.shift(periods=-1, axis=0)['rank']
    tmp['prev2_rank'] = tmp.shift(periods=-2, axis=0)['rank']
    tmp['prev3_rank'] = tmp.shift(periods=-3, axis=0)['rank']

    tmp['prev1_velo'] = tmp.shift(periods=-1, axis=0)['velocity']
    tmp['prev2_velo'] = tmp.shift(periods=-2, axis=0)['velocity']
    tmp['prev3_velo'] = tmp.shift(periods=-3, axis=0)['velocity']
    empty_list.append(tmp)

instrument_to_merge = pd.concat(empty_list)

re_arranged_instrument_to_merge = instrument_to_merge[
    ['date', 'name', 'rank', 'prev1_rank', 'prev2_rank', 'prev3_rank', 'velocity', 'prev1_velo', 'prev2_velo',
     'prev3_velo']]

# 기존 race_result df 에 merge
final_df = merged_df_with_race_info_and_race_result.merge(re_arranged_instrument_to_merge, how='left',
                                                          on=['date', 'name', 'rank', 'velocity'])
# merge 된 df를 출력
final_df.to_pickle(
    '/Users/daham/Desktop/GrowthHackers/horserace/neural-network/combined_df_with_prev_ranks_and_prev_velos.pickle')

# 추가 된 column 만을 출력
final_df[['distance', 'velocity', 'prev1_rank', 'prev2_rank', 'prev3_rank', 'prev1_velo', 'prev2_velo',
          'prev3_velo']].to_pickle(
    '/Users/daham/Desktop/GrowthHackers/horserace/neural-network/columns_df_with_prev_ranks_and_prev_velos.pickle')

