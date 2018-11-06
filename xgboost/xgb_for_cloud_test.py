import numpy as np
import datetime
import category_encoders as ce
from sklearn.model_selection import train_test_split
import xgboost as xgb
import pymysql

db = pymysql.connect(host="SERVER IP", user="root", passwd="PW", db="horserace", charset="utf8")  # SQL 설정
cursor = db.cursor()

cursor.execute("select race_result.code, race_result.date, race_result.round, race_result.lane, race_result.sex, race_result.age,\
                race_result.jockey_w, race_result.rating, race_result.dandivi, race.weather, race.humidity, race.level, race.distance,\
                race.horses, horse.total from race_result, race, horse \
                where race_result.date = race.date and race_result.round = race.round and race_result.code = horse.code")
# 0-5/6-12/13-14
# weather, level one-hot 필요.
# one-hot 후보들: distance, lane, sex
# 최근 3경기 결과, 최근 1개월 내 질병 여부, 거리별 승률 별도로 뽑을 것.

df = np.array(cursor.fetchall())  # array 형태로 받음

le = ce.OneHotEncoder(return_df=False, impute_missing=False, handle_unknown="ignore")

# test = np.array(['a','b','c', 'd']).reshape(-1,1)
# print(le.fit_transform(test))

df = np.append(df, le.fit_transform(df[:, 9]), axis=1)
df = np.append(df, le.fit_transform(df[:, 11]), axis=1)
l
df = np.delete(df, (0, 1, 9, 11), 1)  # index들이랑 one-hot한 column들 날림 - 제대로 되나 잘 모르겠음 ㅎㅎ;
print(df[0])

train, test = train_test_split(df, test_size=0.3, random_state=datetime.datetime.now().second)
real = test[:, 0]
train = xgb.DMatrix(train[:, 1:], label=train[:, 0])  # xgb에서 쓸 수 있게 자료형 변경
test = xgb.DMatrix(test[:, 1:], label=test[:, 0])

# 이제 xgboost 돌리자~
param = {'max_depth': 2, 'eta': 1, 'gamma': 0, 'lambda': 1, 'silent': 1,
         'objective': 'reg:linear'}  # parameter 설정: 공부 필요 - linear??? 만약 각 leaf에서 linear reg 추정이라면 one-hot할 게 훨씬 많아짐
num_round = 2

bst = xgb.train(param, train, num_round)  # train
preds = bst.predict(test)  # test

print(((preds - real) ** 2).mean() ** 0.5)  # rmse 출력