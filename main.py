#for nsetools
from nsetools import Nse
from pprint import pprint
#for quandl
import quandl
# for nsepy
from nsepy import get_history
from nsepy.derivatives import get_expiry_date
from nsepy.live import *
from nsepy import get_quote
from datetime import date
import datetime
# general
import numpy
import math

def predict_expiry_price(index,days_to_prediction, past_years_to_consider):
    quandl.ApiConfig.api_key = "rybokWgFnX5Cwq2jPqzX"
    nse = Nse()
    #fetch a pandas dataframe for Nifty , rdiff gives daily return
    if index == "NIFTY":
        index_data = quandl.get("NSE/NIFTY_50.4", start_date=datetime.date.today()-datetime.timedelta(days=365*past_years_to_consider),end_date=datetime.date.today(),transformation='rdiff')
        ind = nse.get_index_quote('NIFTY 50')
    elif index == "BANK_NIFTY":
        index_data = quandl.get("NSE/NIFTY_BANK.4", start_date=datetime.date.today()-datetime.timedelta(days=365*past_years_to_consider), end_date=datetime.date.today(), transformation='rdiff')
        ind = nse.get_index_quote('NIFTY BANK')
    #select the closing price into a dataframe
    print("total sample size :",index_data.count())
    # print(index_data)
    closing_price_data = index_data[['Close']]
    closing_price_data.index.name = None
    # calculate the standard deviation on daily returns
    stddev= closing_price_data.std()*100
    # stddev = numpy.std(newdf['Close'])
    # print("standard deviation:",stddev)
    daily_mean_return=closing_price_data.mean()*100
    # print("daily average return:", daily_mean_return)
    higher_bound_percentage = daily_mean_return*days_to_prediction + stddev*math.sqrt(days_to_prediction)
    lower_bound_percentage = daily_mean_return*days_to_prediction - stddev*math.sqrt(days_to_prediction)
    # print(higher_bound_percentage)
    # print(lower_bound_percentage)
    print(ind['lastPrice'])
    upside_potential = (ind['lastPrice'] * higher_bound_percentage/100)
    print("upper target: ", ind['lastPrice'] + upside_potential)
    downside_potential = (ind['lastPrice'] * lower_bound_percentage/100)
    print("lower target: ", ind['lastPrice'] + downside_potential)
    # print(nifty_data.tail(1))

def check_consecutive_occurences(past_years_to_consider):
    quandl.ApiConfig.api_key = "rybokWgFnX5Cwq2jPqzX"
    nse = Nse()
    # fetch a pandas dataframe for Nifty , rdiff gives daily return
    index="NIFTY"
    if index == "NIFTY":
        index_data = quandl.get("NSE/NIFTY_50.4", start_date=datetime.date.today() - datetime.timedelta(days=365 * past_years_to_consider), end_date=datetime.date.today(), transformation='rdiff')
        ind = nse.get_index_quote('NIFTY 50')
    elif index == "BANK_NIFTY":
        index_data = quandl.get("NSE/NIFTY_BANK.4", start_date=datetime.date.today() - datetime.timedelta(days=365 * past_years_to_consider), end_date=datetime.date.today(), transformation='rdiff')
        ind = nse.get_index_quote('NIFTY BANK')
    # print(index_data)
    #consecutive down days or updays trend predictor (gives probability)
    print("total sample size :", index_data.count())
    consecutive_neg_count = 0
    consecutive_neg_occurences = 0
    for index, row in index_data.iterrows():
        if row['Close'] * 100 <= 0:
            consecutive_neg_count = consecutive_neg_count + 1
        else:
            consecutive_neg_count = 0
        if consecutive_neg_count > 3:
            print(index)
            consecutive_neg_occurences = consecutive_neg_occurences + 1
            consecutive_neg_count = 0
    print("Consecutive 4-day negative occurences : ", consecutive_neg_occurences)

    #bucking the trend after n days predictor
    trend_flip_day_num = 5
    trend_flip_count = 0
    trend_not_flip_count = 0
    day_count = 0
    #for red days
    for index, row in index_data.iterrows():
        if day_count == trend_flip_day_num-1:
            if row['Close'] * 100 < 0:
                trend_flip_count = trend_flip_count + 1
            else:
                trend_not_flip_count = trend_not_flip_count + 1
            day_count  = 0
            continue
        if row['Close'] * 100 < 0:
            day_count=day_count+1
        else:
            day_count = 0
    day_count = 0
    print("trend_flip_count:", trend_flip_count)
    print("trend_not_flip_count:", trend_not_flip_count)
    #for green days
    for index, row in index_data.iterrows():
        if day_count == trend_flip_day_num-1:
            if row['Close'] * 100 > 0:
                trend_flip_count = trend_flip_count + 1
            else:
                trend_not_flip_count = trend_not_flip_count + 1
            day_count  = 0
            continue
        if row['Close'] * 100 > 0:
            day_count=day_count+1
        else:
            day_count = 0

    print("trend_flip_count:",trend_flip_count)
    print("trend_not_flip_count:",trend_not_flip_count)

def run_nsetools():
    nse = Nse()
    # print(nse)
    q = nse.get_quote('NOCIL')
    #prints a dictionary of all data
    # pprint(q)
    ind = nse.get_index_quote('NIFTY 50')
    #pprint(ind['lastPrice'])
    ind_codes = nse.get_index_list()
    #pprint(ind_codes)

def run_nsepy():
    nse = Nse()
    ind = nse.get_index_quote('NIFTY 50')
    current_price = ind['lastPrice']
    if current_price%50 <= 25:
        atm_strike = (int)(current_price - current_price%50)
    else:
        atm_strike = (int)(current_price + (50 - current_price%50))
    print(atm_strike)
    expiry = atm_strike-100
    print("expiry: ",expiry)
    weekend = False

    if weekend == True:
        evaluation_date = date(2017,11,7)
    else:
        evaluation_date = datetime.date.today()
    # call option quote
    df = get_history(symbol="NIFTY",start=evaluation_date,end=evaluation_date,index=True,option_type='CE',strike_price=atm_strike,expiry_date=get_expiry_date(year=2017,month=11))
    call_premium = df[['Last']]
    print(call_premium)
    call_option_payoff = -call_premium + max(0,expiry-atm_strike)
    # put option quotecall_premium
    df2 = get_history(symbol="NIFTY", start=evaluation_date, end=evaluation_date, index=True, option_type='PE',strike_price=atm_strike, expiry_date=get_expiry_date(year=2017, month=11))
    put_premium = df2[['Last']]
    print(put_premium)
    put_option_payoff = put_premium - max(0,atm_strike-expiry)
    #equity quote
    df3 = get_history(symbol="NIFTY",start=evaluation_date,end=evaluation_date,index=True)
    live_price = df3[['Close']]
    #futures quote
    df4 = get_history(symbol="NIFTY",start=evaluation_date,end=evaluation_date,index=True,futures=True,expiry_date=get_expiry_date(2017,11))
    futures_price = df4[['Last']]
    futures_payoff = futures_price - expiry
    print(futures_price)

    net_payoff = call_option_payoff + put_option_payoff + futures_payoff
    print("net payoff: ",net_payoff)
    # df4 = get_quote(symbol="NIFTY",series='EQ')
    # print(df4)

def main():
    choice = "predict_expiry" # "predict_expiry" or "check_occurences" or "nsepy" or "nsetools"
    days_to_prediction = 2
    past_years_to_consider = 2
    index = "BANK_NIFTY" # "BANK_NIFTY" or "NIFTY"

    if choice == "predict_expiry":
        predict_expiry_price(index,days_to_prediction,past_years_to_consider)
    elif choice == "check_occurences":
        check_consecutive_occurences(past_years_to_consider)
    elif choice == "nsetools":
        run_nsetools()
    else:
        run_nsepy()

if __name__ == "__main__" :
    main()

