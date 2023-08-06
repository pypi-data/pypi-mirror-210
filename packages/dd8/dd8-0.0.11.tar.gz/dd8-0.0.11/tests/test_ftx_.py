import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dd8.connectivity.crypto.ftx_ as ftx_
import dd8.connectivity.crypto.enums as enums
import dd8.finance.technical_analysis as ta


if __name__ == '__main__':

    # get market data
    symbol = 'BTC-PERP'
    resolution = enums.ENUM_RESOLUTION.MINUTE_15.value
    
    start_datetime = ftx_.to_timestamp('15 Oct 2020 08:00')
    end_datetime = ftx_.to_timestamp('16 Oct 2022 08:00')

    client = ftx_.FtxMarketData()
    data = client.get_historical(symbol, 
                                 resolution, 
                                 start_datetime, 
                                 end_datetime)

    # generate technical indicators
    for i in range(17):            
        roc = ta.RateOfChange(period=1, shift=int(i), uid = 'returns_period_1_shift_{shift}'.format(shift=int(i)))    
        data.extend(roc.uid, roc.fit(data.close()))
    

    
    # roc = ta.RateOfChange(period=1, shift=0, uid = 'volume_period_1_shift_0')    
    # data.extend(roc.uid, roc.fit(data.volume()))

    # roc = ta.RateOfChange(period=28, shift=0, uid = 'volume_period_28_shift_0')    
    # data.extend(roc.uid, roc.fit(data.volume()))

    # roc = ta.RateOfChange(period=56, shift=0, uid = 'volume_period_56_shift_0')    
    # data.extend(roc.uid, roc.fit(data.volume()))

    # rsi = ta.RelativeStrengthIndex(period=14, shift=0, uid='rsi_14')
    # data.extend(rsi.uid, rsi.fit(data.close()))

    # rsi = ta.RelativeStrengthIndex(period=21, shift=0, uid='rsi_21')
    # data.extend(rsi.uid, rsi.fit(data.close()))
    
    # rsi = ta.RelativeStrengthIndex(period=21, shift=0, uid='rsi_28')
    # data.extend(rsi.uid, rsi.fit(data.close()))

    # rsi = ta.RelativeStrengthIndex(period=35, shift=0, uid='rsi_35')
    # data.extend(rsi.uid, rsi.fit(data.close()))

    # stdev = ta.StandardDeviation(period=14, demean=True, uid='stdev_period_14')    
    # data.extend(stdev.uid, stdev.fit(data._slice('returns_period_1_shift_0', -99, -99)))

    # stdev = ta.StandardDeviation(period=28, demean=True, uid='stdev_period_28')    
    # data.extend(stdev.uid, stdev.fit(data._slice('returns_period_1_shift_0', -99, -99)))

    # stdev = ta.StandardDeviation(period=56, demean=True, uid='stdev_period_56')    
    # data.extend(stdev.uid, stdev.fit(data._slice('returns_period_1_shift_0', -99, -99)))

    classes = [(i, (10*i+(-50))/10000) for i in range(11)]
    classes = [(0,-0.0025), (1, 0.0) , (2, 0.0025)]
    label = ta.Label(classes, uid='class')
    data.extend(label.uid, label.fit(data._slice('returns_period_1_shift_0', -99, -99)))

    data.to_csv(symbol+'.csv')

    