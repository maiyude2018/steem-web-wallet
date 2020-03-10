# coding=utf-8
import streamlit as st
from api import Api
import threading
from beem.steem import Steem
from beem.account import Account
import pandas as pd
from steemengine.wallet import Wallet
import hashlib
from binascii import hexlify
from beembase.transactions import Signed_Transaction
from beem.instance import set_shared_steem_instance
import numpy as np
import time

nodes = ['https://api.steemit.com']
#df = "1"
#st.dataframe(df)

api=Api()
local_values = threading.local()
@st.cache()
def acc(player):
    sp=sp_de=voting=down=rc=steem_balance=sbd_balance=0
    try:
        #获取SP
        acc = Account(player)
        sp = acc.get_steem_power()
        sp=int(sp)
        print(sp,"SP")

        #详细SP信息
        if player != "":
            account = Account(player)
            get_balance = account.balances
            steem_balance = get_balance["available"][0]
            sbd_balance = get_balance["available"][1]
            steem_balance = str(steem_balance).replace("STEEM", "")
            steem_balance = float(steem_balance)
            sbd_balance = str(sbd_balance).replace("SBD", "")
            sbd_balance = float(sbd_balance)
            sp_all = get_balance["available"][2]
            sp_de = acc.steem.vests_to_sp(sp_all)
            sp_de = int (sp_de)
            print(sp_de, "SP")



        #点赞能量#踩能量
        voting, down=api.get_upanddown(player)
        print(voting)
        print(down)

        try:
            rc = api.get_player_vp(player)
            rc = int(rc)
        except Exception as e:
            print(e)
            rc = 0


    except Exception as e:
        print(e)
        sp=sp_de=voting=down=rc=steem_balance=sbd_balance=0
    return sp,sp_de,voting,down,rc,steem_balance,sbd_balance


@st.cache()
def scot(player,steem_balance, sbd_balance):
    token = ["STEEM", "SBD"]
    scot_balance = [steem_balance, sbd_balance]
    if player !="":
        wallet = Wallet(player)
        scot = wallet.get_balances()
        for i in scot:
            if float(i["balance"]) > 0:
                token.append(i["symbol"])
                scot_balance.append(i["balance"])
        print(token)
        print(scot_balance)
    return token,scot_balance

# steem-engines转账token到某人
def transfer_to_someone(key,token, name, toplayer, money,memo):
    local_values.s = Steem(keys=[key])
    contract_payload = {'symbol': token, 'to': toplayer, 'quantity': str(money), 'memo': memo}
    json_data = {'contractName': 'tokens', 'contractAction': 'transfer', 'contractPayload': contract_payload}
    kk = local_values.s.custom_json('ssc-mainnet1', json_data, required_auths=[name])

    tx = Signed_Transaction(kk)
    tx.data.pop("signatures", None)
    print(tx)
    h = hashlib.sha256(bytes(tx)).digest()
    transaction_id = hexlify(h[:20]).decode("ascii")
    print(transaction_id)
    url = "https://steemd.com/tx/%s" % transaction_id
    print(url)
    print("转账完成")
    return url

def steem_sbd(key,player,token,mymoney,toplayer,memo):
    local_values.s = Steem(keys=[key])
    set_shared_steem_instance(local_values.s)
    account = Account(player)
    # 转账
    kk=account.transfer(toplayer,mymoney, token,memo)

    tx = Signed_Transaction(kk)
    tx.data.pop("signatures", None)
    print(tx)
    h = hashlib.sha256(bytes(tx)).digest()
    transaction_id = hexlify(h[:20]).decode("ascii")
    print(transaction_id)
    url = "https://steemd.com/tx/%s" % transaction_id
    print("转账完成")
    print(url)
    return url

def daili(key,player,toplayer,sp):
    local_values.s = Steem(keys=[key])
    acc = Account(player, steem_instance=local_values.s)
    resp = acc.delegate_vesting_shares(
        toplayer,
        local_values.s .sp_to_vests(sp),
        account=player
    )

    print(resp)

def votewitness(key,name,approve=True):
    s = Steem(keys=[key])
    acc = Account(player, steem_instance=s)
    list=name
    w=acc.approvewitness(list,approve=approve)
    print(w)


#左侧
key = st.text('手机端左侧点开有账户信息')
st.title("steem网页轻钱包")
player = st.text_input('请输入账户')
key = st.text_input('如果需要转账,请输入active key(仅查询可留空)')
#if key != "":
#    s = Steem(keys=[key,key])
#else:
#    s = Steem()

#获取信息

sp,sp_de,voting,down,rc,steem_balance,sbd_balance=acc(player)
option2 = st.sidebar.selectbox(
    '功能选项',
     ['转账Transfer',"开发中功能development"])
#点赞权重
sps = st.sidebar.subheader("点赞权重(Vote Weight)")
sp_sp = st.sidebar.header(str(sp)+" SP")
sp_text = st.sidebar.text("steem power："+str(sp_de)+" SP")

#左侧VP显示
votings=st.sidebar.header("点赞能量Voting Power")
voting_progress = st.sidebar.progress(int(voting))
voting_text=st.sidebar.text(str(voting)+"%")

#Downvote Power
downvotePower=st.sidebar.header("踩人能量Downvote Power")
downvotePower_progress = st.sidebar.progress(int(down))
downvotePower_text=st.sidebar.text(str(down)+"%")

#Resource Credits
rcs=st.sidebar.header("资源能量Resource Credits")
rc_progress = st.sidebar.progress(rc)
rc_text=st.sidebar.text(str(rc)+"%")

#player="maiyude"

#if player !="":
bala = st.sidebar.header("钱包balance")
token,scot_balance=scot(player,steem_balance, sbd_balance)

df = pd.DataFrame({'数量balance': scot_balance,
                   '币种Token': token
                   })
df.index=df.index+1
print(df)
option3 = st.sidebar.table(df)


if option2 == "转账Transfer":
    #中间菜单
    st.progress(100)
    st.subheader("转账Transfer")
    toplayer = st.text_input('转到to')
    Token=st.text_input('转账币种Token')
    Token=Token.upper()
    number=st.text_input('数量Number')
    memo = st.text_input('备忘memo(可留空)')
    button_trans=st.button('提交')

    # 当按下button_trans按钮的事件
    if button_trans:
        key2 = st.sidebar.text_input('请输入active key2')
        print("转账开始")
        if key != "":
            st.write('转账开始')
            try:
                if Token == "STEEM" or Token == "SBD":
                    number = float(number)
                    print(Token, number)
                    thread2 = threading.Thread(target=steem_sbd, args=(key, player, Token, number, toplayer, memo))
                    with st.spinner('Wait for it...'):
                        thread2.start()
                        thread2.join()
                    st.write('转账完成')
                    st.balloons()

                else:
                    print("scot转账")
                    print(Token, number)
                    print(Token, player, toplayer, number, memo)
                    thread1 = threading.Thread(target=transfer_to_someone,args=(key, Token, player, toplayer, number, memo))
                    with st.spinner('Wait for it...'):
                        thread1.start()
                        thread1.join()
                    st.write('转账完成')
                    st.balloons()
                    pass
            except Exception as e:
                st.write('错误')
                st.write(e)
        else:
            st.write('## 请输入active key！')


    st.progress(100)

    st.subheader("委派SP(delegate SP)")
    sp_toplayer = st.text_input('委派给谁to')
    sp_number = st.text_input('数量Number.')
    button_sp = st.button('委派SP')
    # 当按下button_sp按钮的事件
    if button_sp:
        if key !="":

            if sp_toplayer != "" and sp_number != "":
                print("开始委派SP")
                st.write('开始委派SP')
                sp_number = float(sp_number)
                thread3 = threading.Thread(target=daili, args=(key, player, sp_toplayer, sp_number))
                with st.spinner('Wait for it...'):
                    thread3.start()
                    thread3.join()
                st.write('委派完成')
                st.balloons()
        else:
            st.write('## 请输入active key！')


    st.progress(100)

    st.subheader("投票见证人Approvewitness")
    witnesses_toplayer = st.text_input('投票给谁to',"maiyude")
    option_wit = st.selectbox("",['投票Approve', "撤票Return"])
    if option_wit == "投票Approve":
        app_choise=True
    else:
        app_choise=False
    button_witnesses = st.button('提交Approve')
    # 当按下button_witness按钮的事件
    if button_witnesses:
        if key !="":
            st.write('投票中……')
            if witnesses_toplayer != "":
                thread4 = threading.Thread(target=votewitness, args=(key, witnesses_toplayer,app_choise))
                with st.spinner('Wait for it...'):
                    thread4.start()
                    thread4.join()
                st.write('完成')
                st.balloons()
        else:
            st.write('## 请输入active key！')
    st.progress(100)









if option2 == "开发中功能development":
    st.title("更多功能开发中…………")








