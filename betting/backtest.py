# back test에 필요한 함수

# 데이터 가공
# 필요한 데이터만 선택하여 계산속도 향상
# 결측치가 많은 경우 유효하지 않은 게임으로 판단
def getData(df, col_list, groupid, min_size=10):
    data = df[col_list]

    gb_data = data.groupby([groupid])
    gb_data = [gb_data.get_group(x) for x in gb_data.groups]

    total_data = []
    for g in gb_data:
        if len(g) >= min_size:
            total_data.append(g)
    
    return data, gb_data, total_data

# 단승식 베팅
def dan_bet(bet, start, total_data, pred_row_name, ascendingTF=False, min_pred=0.15):
    money = start
    moneylist = [start]

    ongoing=0
    get=0
    cnt=0

    for game in total_data:
        winner = game[game['rank'] == 1] # 실제 1등 말
        wish   = game[game[pred_row_name].rank(ascending=ascendingTF) == 1] # 예측 1등말

        # 1등말 없는 경우!
        if winner.empty or wish.empty:
            ongoing+=1
            moneylist.append(money)
            continue

        # predict의 값이 낮은 경우 제외
        # XGBoost에서는 등수를 예측하므로 사용되지 않는다.
        if wish.iloc[0][pred_row_name] < min_pred:
            moneylist.append(money)
            continue

        cnt+=1
        money-=bet

        # RANK 비교
        if wish.iloc[0]['rank'] == winner.iloc[0]['rank']:
            money += bet * winner.iloc[0]['dandivi']
            get+=1
        moneylist.append(money)

        # 돈을 다 쓴 경우 베팅 종료
        if money<0:
            break

    return ongoing, cnt, get, moneylist


# 연승 베팅
def yeon_bet(bet,start,total_data,pred_row_name,ascendingTF=False,min_pred=0.15):
    money = start
    moneylist = [start]

    ongoing=0
    get=0
    cnt=0

    for game in total_data:
        winner = game[game['rank'] == 1] # 실제 1등 말
        winner2 = game[game['rank'] == 2] # 실제 2등 말
        winner3 = game[game['rank'] == 3] # 실제 3등 말
        wish   = game[game[pred_row_name].rank(ascending=ascendingTF) == 1] # 예측 1등말

        # 1,2,3등말 없는 경우!
        if winner.empty or winner2.empty or winner3.empty or wish.empty:
            ongoing+=1
            moneylist.append(money)
            continue

        if wish.iloc[0][pred_row_name] < min_pred:
            moneylist.append(money)
            continue

        cnt+=1
        money-=bet

        # RANK 비교
        if wish.iloc[0]['rank'] in [winner.iloc[0]['rank'], winner2.iloc[0]['rank'], winner3.iloc[0]['rank']]:
            money += bet * wish.iloc[0]['yeondivi']
            get+=1
        moneylist.append(money)
        ongoing+=1


        if money<0:
            break

    return ongoing, cnt, get, moneylist    
    
# 켈리베팅 - 단승    
def kelly_dan_bet(bet, start, total_data, pred_row_name, ascendingTF=False, min_pred=0.15):
    money = start
    moneylist = [start]

    ongoing=0
    get=0
    cnt=0

    for game in total_data:
        winner = game[game['rank'] == 1] # 실제 1등 말
        wish   = game[game[pred_row_name].rank(ascending=ascendingTF) == 1] # 예측 1등말

        # 1등말 없는 경우!
        if winner.empty or wish.empty:
            ongoing+=1
            moneylist.append(money)
            continue

        # 켈리베팅 공식!
        # proportion = (BP-Q)/B
        # 베팅금액 = proportion * 현재자산
        # proportion > 0 인 경우에만 베팅
        kelly_B = wish.iloc[0]['dandivi']-1
        kelly_P = wish.iloc[0][pred_row_name]
        prop = (kelly_B * kelly_P - (1-kelly_P)) / kelly_B
        if prop<0:
            continue
        cnt+=1
        bet = prop * money
        money-=bet

        # RANK 비교
        if wish.iloc[0]['rank'] == winner.iloc[0]['rank']:
            money += bet * winner.iloc[0]['dandivi']
            get+=1
        moneylist.append(money)
        ongoing+=1


        if money<0:
            break

    return ongoing, cnt, get, moneylist

# 켈리 베팅 - phat이 높은 3개의 말
def kelly_dan3_bet(bet, start, total_data, pred_row_name, ascendingTF=False, min_pred=0.15):
    money = start
    moneylist = [start]

    ongoing=0
    get=0
    cnt=0

    for game in total_data:
        winner = game[game['rank'] == 1] # 실제 1등 말
        wish   = game[game[pred_row_name].rank(ascending=ascendingTF) == 1] # 예측 1등말
        wish2  = game[game[pred_row_name].rank(ascending=ascendingTF) == 2] # 예측 2등말
        wish3  = game[game[pred_row_name].rank(ascending=ascendingTF) == 3] # 예측 3등말

        # 1등말 없는 경우!
        if winner.empty:
            ongoing+=1
            moneylist.append(money)
            continue

        for w in [wish, wish2, wish3]:
            kelly_B = w.iloc[0]['dandivi']-1
            kelly_P = w.iloc[0][pred_row_name]
            prop = (kelly_B * kelly_P - (1-kelly_P)) / kelly_B
            if prop<0:
                continue
            cnt+=1
            bet = prop * money
            money-=bet

            # RANK 비교
            if w.iloc[0]['rank'] == winner.iloc[0]['rank']:
                money += bet * winner.iloc[0]['dandivi']
                get+=1
            moneylist.append(money)
            ongoing+=1


        if money<0:
            break

    return ongoing, cnt, get, moneylist


# 켈리 베팅 - 연승. phat 별 예측률 반영
def kelly_yeon_bet(bet, start, total_data, pred_row_name, ascendingTF=False, min_pred=0.15):
    money = start
    moneylist = [start]

    ongoing=0
    get=0
    cnt=0

    for game in total_data:
        winner = game[game['rank'] == 1] # 실제 1등 말
        wish   = game[game[pred_row_name].rank(ascending=ascendingTF) == 1] # 예측 1등말

        # 1등말 없는 경우!
        if winner.empty or wish.empty:
            ongoing+=1
            moneylist.append(money)
            continue

        kelly_B = wish.iloc[0]['yeondivi']-0.5
        if kelly_B <=0:
            continue
        prediction = wish.iloc[0][pred_row_name]
        pred_list = [0.15, 0.2, 0.25, 1]
        prop_list = [0.476, 0.559, 0.701, 0.813]
        for pl in range(len(pred_list)):
            if prediction < pred_list[pl]:
                kelly_P=prop_list[pl]
                break
        kelly_P = wish.iloc[0][pred_row_name]
        prop = (kelly_B * kelly_P - (1-kelly_P)) / kelly_B
        if prop<0:
            continue
        cnt+=1
        bet = prop * money
        money-=bet

        # RANK 비교
        if wish.iloc[0]['rank'] == winner.iloc[0]['rank']:
            money += bet * winner.iloc[0]['yeondivi']
            get+=1
        moneylist.append(money)
        ongoing+=1


        if money<0:
            break

    return ongoing, cnt, get, moneylist

# 켈리 베팅 - 연승, phat 상위 3개 말. phat 별 예측률 반영
def kelly_yeon3_bet(bet, start, total_data, pred_row_name, ascendingTF=False, min_pred=0.15):
    money = start
    moneylist = [start]

    ongoing=0
    get=0
    cnt=0

    for game in total_data:
        winner = game[game['rank'] == 1] # 실제 1등 말
        wish   = game[game[pred_row_name].rank(ascending=ascendingTF) == 1] # 예측 1등말
        wish2  = game[game[pred_row_name].rank(ascending=ascendingTF) == 2] # 예측 2등말
        wish3  = game[game[pred_row_name].rank(ascending=ascendingTF) == 3] # 예측 3등말

        # 1등말 없는 경우!
        if winner.empty:
            ongoing+=1
            moneylist.append(money)
            continue

        for w in [wish, wish2, wish3]:
            kelly_B = w.iloc[0]['yeondivi']-0.5
            if kelly_B <=0:
                continue
            prediction = wish.iloc[0][pred_row_name]
            pred_list = [0.15, 0.2, 0.25, 1]
            prop_list = [0.476, 0.559, 0.701, 0.813]
            for pl in range(len(pred_list)):
                if prediction < pred_list[pl]:
                    kelly_P=prop_list[pl]
                    break
            kelly_P = w.iloc[0][pred_row_name]
            prop = (kelly_B * kelly_P - (1-kelly_P)) / kelly_B
            if prop<0:
                continue
            cnt+=1
            bet = prop * money
            money-=bet

            # RANK 비교
            if w.iloc[0]['rank'] == winner.iloc[0]['rank']:
                money += bet * winner.iloc[0]['yeondivi']
                get+=1
            moneylist.append(money)
            ongoing+=1


        if money<0:
            break

    return ongoing, cnt, get, moneylist

# 켈리베팅 in Neural Network - 단승    
# Neural Network에서 prediction은 확률이 아니므로 예측률을 직접 계산하여 반영한다.
def kelly_nn_dan_bet(bet, start, total_data, pred_row_name, ascendingTF=False, min_pred=0.15):
    money = start
    moneylist = [start]

    ongoing=0
    get=0
    cnt=0

    for game in total_data:
        winner = game[game['rank'] == 1] # 실제 1등 말
        wish   = game[game[pred_row_name].rank(ascending=ascendingTF) == 1] # 예측 1등말

        # 1등말 없는 경우!
        if winner.empty or wish.empty:
            ongoing+=1
            moneylist.append(money)
            continue

        # 켈리베팅 공식!
        # proportion = (BP-Q)/B
        # 베팅금액 = proportion * 현재자산
        # proportion > 0 인 경우에만 베팅
        kelly_B = wish.iloc[0]['dandivi']-1
        prediction = wish.iloc[0][pred_row_name]
        pred_list = [0.5, 0.6, 0.7, 1]
        prop_list = [0.137, 0.327, 0.388, 0.494]
        for pl in range(len(pred_list)):
            if prediction < pred_list[pl]:
                kelly_P=prop_list[pl]
                break

        prop = (kelly_B * kelly_P - (1-kelly_P)) / kelly_B
        if prop<0:
            continue
        cnt+=1
        bet = prop * money
        money-=bet

        # RANK 비교
        if wish.iloc[0]['rank'] == winner.iloc[0]['rank']:
            money += bet * winner.iloc[0]['dandivi']
            get+=1
        moneylist.append(money)
        ongoing+=1


        if money<0:
            break

    return ongoing, cnt, get, moneylist

# 켈리 베팅 in Neural Network - phat이 높은 3개의 말
def kelly_nn_dan3_bet(bet, start, total_data, pred_row_name, ascendingTF=False, min_pred=0.15):
    money = start
    moneylist = [start]

    ongoing=0
    get=0
    cnt=0

    for game in total_data:
        winner = game[game['rank'] == 1] # 실제 1등 말
        wish   = game[game[pred_row_name].rank(ascending=ascendingTF) == 1] # 예측 1등말
        wish2  = game[game[pred_row_name].rank(ascending=ascendingTF) == 2] # 예측 2등말
        wish3  = game[game[pred_row_name].rank(ascending=ascendingTF) == 3] # 예측 3등말

        # 1등말 없는 경우!
        if winner.empty:
            ongoing+=1
            moneylist.append(money)
            continue

        for w in [wish, wish2, wish3]:
            kelly_B = w.iloc[0]['dandivi']-1
            prediction = wish.iloc[0][pred_row_name]
            pred_list = [0.5, 0.6, 0.7, 1]
            prop_list = [0.137, 0.327, 0.388, 0.494]
            for pl in range(len(pred_list)):
                if prediction < pred_list[pl]:
                    kelly_P=prop_list[pl]
                    break
            prop = (kelly_B * kelly_P - (1-kelly_P)) / kelly_B
            if prop<0:
                continue
            cnt+=1
            bet = prop * money
            money-=bet

            # RANK 비교
            if w.iloc[0]['rank'] == winner.iloc[0]['rank']:
                money += bet * winner.iloc[0]['dandivi']
                get+=1
            moneylist.append(money)
            ongoing+=1


        if money<0:
            break

    return ongoing, cnt, get, moneylist


# 켈리 베팅 in Neural Network - 연승
def kelly_nn_yeon_bet(bet, start, total_data, pred_row_name, ascendingTF=False, min_pred=0.15):
    money = start
    moneylist = [start]

    ongoing=0
    get=0
    cnt=0

    for game in total_data:
        winner = game[game['rank'] == 1] # 실제 1등 말
        wish   = game[game[pred_row_name].rank(ascending=ascendingTF) == 1] # 예측 1등말

        # 1등말 없는 경우!
        if winner.empty or wish.empty:
            ongoing+=1
            moneylist.append(money)
            continue

        kelly_B = wish.iloc[0]['yeondivi']-1
        if kelly_B <= 0:
            continue
        prediction = wish.iloc[0][pred_row_name]
        pred_list = [0.5, 0.6, 0.7, 1]
        prop_list = [0.474, 0.633, 0.733, 0.776]
        for pl in range(len(pred_list)):
            if prediction < pred_list[pl]:
                kelly_P=prop_list[pl]
                break
        prop = (kelly_B * kelly_P - (1-kelly_P)) / kelly_B
        if prop<0:
            continue
        cnt+=1
        bet = prop * money
        money-=bet

        # RANK 비교
        if wish.iloc[0]['rank'] == winner.iloc[0]['rank']:
            money += bet * winner.iloc[0]['yeondivi']
            get+=1
        moneylist.append(money)
        ongoing+=1


        if money<0:
            break

    return ongoing, cnt, get, moneylist

# 켈리 베팅 in Neural Network - 연승, phat 상위 3개 말
def kelly_nn_yeon3_bet(bet, start, total_data, pred_row_name, ascendingTF=False, min_pred=0.15):
    money = start
    moneylist = [start]

    ongoing=0
    get=0
    cnt=0

    for game in total_data:
        winner = game[game['rank'] == 1] # 실제 1등 말
        wish   = game[game[pred_row_name].rank(ascending=ascendingTF) == 1] # 예측 1등말
        wish2  = game[game[pred_row_name].rank(ascending=ascendingTF) == 2] # 예측 2등말
        wish3  = game[game[pred_row_name].rank(ascending=ascendingTF) == 3] # 예측 3등말

        # 1등말 없는 경우!
        if winner.empty:
            ongoing+=1
            moneylist.append(money)
            continue

        for w in [wish, wish2, wish3]:
            kelly_B = w.iloc[0]['yeondivi']-1
            if kelly_B <=0:
                continue
            prediction = wish.iloc[0][pred_row_name]
            pred_list = [0.5, 0.6, 0.7, 1]
            prop_list = [0.474, 0.633, 0.733, 0.776]
            for pl in range(len(pred_list)):
                if prediction < pred_list[pl]:
                    kelly_P=prop_list[pl]
                    break
            kelly_P = w.iloc[0][pred_row_name]
            prop = (kelly_B * kelly_P - (1-kelly_P)) / kelly_B
#            print(cnt, prop)
            if prop<0:
                continue
            cnt+=1
            bet = prop * money
            money-=bet

            # RANK 비교
            if w.iloc[0]['rank'] == winner.iloc[0]['rank']:
                money += bet * winner.iloc[0]['yeondivi']
                get+=1
            moneylist.append(money)
            ongoing+=1


        if money<0:
            break

    return ongoing, cnt, get, moneylist
