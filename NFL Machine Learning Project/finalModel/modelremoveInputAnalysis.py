from os import X_OK
from pickle import UnpicklingError
import pandas as pd
import  csv
from keras.models import load_model
import numpy as np
import scipy.io
import tensorflow as tf
import keras
from numpy import asarray
from pandas import read_csv
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Normalizer
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence
from sklearn.metrics import mean_squared_error
import math
# fix random seed for reproducibility
np.random.seed(7)

pad_length = 1500

workDirectory = 'E:\\All File\\'
lastWeek = pd.read_csv(workDirectory + "nflData\\week9.csv", low_memory=False)
gameMax = lastWeek['gameId'].max()
weekPicklePath = workDirectory + "week_2_5_7_9.pkl"
playPicklePath = workDirectory + "play_all.pkl"
modPicklePath = workDirectory + "modPlays_2_5_7_9.pk1"


pickle = True
try:
    foo = pd.read_pickle(weekPicklePath)
except (OSError, IOError, FileNotFoundError) as e:
    pickle = False


print("starting data preparation")

playersData = pd.read_csv(workDirectory + "nflData\\players.csv")
mapping = {'5-6': 5*12+6, '5-7': 5*12+7, '5-8': 5*12+8, '5-9': 5*12+9, '5-10': 5*12+10, '5-11': 5*12+11, '6-0': 6*12, '6-1': 6*12+1, '6-2': 6*12+2, '6-3': 6*12+3, '6-4': 6*12+4, '6-5': 6*12+5, '6-6': 6*12+6, '6-7': 6*12+7}
playersData = playersData.replace({'height': mapping})



if(pickle):
    week = foo
else:
    print("week pickle not found")
    week1 = pd.read_csv(workDirectory + "nflData\\week1.csv", low_memory=False)
    # week2 = pd.read_csv(workDirectory + "nflData\\week2.csv", low_memory=False)
    # week3 = pd.read_csv(workDirectory + "nflData\\week3.csv", low_memory=False)
    #week4 = pd.read_csv(workDirectory + "nflData\\week4.csv", low_memory=False)
#week5 = pd.read_csv(workDirectory + "nflData\\week5.csv", low_memory=False)
#week6 = pd.read_csv(workDirectory + "nflData\\week6.csv", low_memory=False)
#week7 = pd.read_csv(workDirectory + "nflData\\week7.csv", low_memory=False)
#week8 = pd.read_csv(workDirectory + "nflData\\week8.csv", low_memory=False)
#week9 = pd.read_csv(workDirectory + "nflData\\week9.csv", low_memory=False)
#week10 = pd.read_csv(workDirectory + "nflData\\week10.csv", low_memory=False)
#week11 = pd.read_csv(workDirectory + "nflData\\week11.csv", low_memory=False)
#week12 = pd.read_csv(workDirectory + "nflData\\week12.csv", low_memory=False)
#week13 = pd.read_csv(workDirectory + "nflData\\week13.csv", low_memory=False)
#week14 = pd.read_csv(workDirectory + "nflData\\week14.csv", low_memory=False)
#week15 = pd.read_csv(workDirectory + "nflData\\week15.csv", low_memory=False)
#week16 = pd.read_csv(workDirectory + "nflData\\week16.csv", low_memory=False)
    #week17 = pd.read_csv(workDirectory + "nflData\\week17.csv", low_memory=False)
#week =  pd.concat([week1, week2, week3, week4, week5, week6, week7, week8, week9, week10, week11, week12, week13, week14, week15, week16, week17], ignore_index=True)
    week =  pd.concat([week1], ignore_index=True)

    week = week[(week['gameId'] <= gameMax) & (week['playDirection'].str.contains('left'))]
    week = week[["gameId", "playId", "frameId", "nflId", "x","y","s", "a", "dis", "o", "dir", "team", "position", "route"]]
    #print(week)
    values = {'o': -1, 'dir': -1, 'route': 'NA', 'nflId': 0}
    week.fillna(value=values)
    #print(pd.get_dummies(week, prefix='r', columns = ['route']))
    oneHotroute = pd.get_dummies(week, prefix='r', columns = ['route'])
    oneHotPos = pd.get_dummies(oneHotroute, prefix='pos', columns = ['position'])
    week = pd.get_dummies(oneHotPos, prefix='team', columns = ['team']) #one hot encoding team / football
    week.to_pickle(weekPicklePath)

try:
    plays = pd.read_pickle(playPicklePath)
except (OSError, IOError, FileNotFoundError) as e:
    print("plays pickle not found")
    plays = pd.read_csv(workDirectory + "nflData\\plays.csv", low_memory=False)
    plays.to_pickle(playPicklePath)

try:
    modPlays = pd.read_pickle(modPicklePath)
    playVarList = list(modPlays)
except (OSError, IOError, FileNotFoundError) as e:
    print("modPlays pickle not found")
    mod = plays[plays["gameId"] <= gameMax]
    mod = mod[['gameId', 'playId', 'offensePlayResult', 'down', 'yardsToGo', 'yardlineNumber', 'defendersInTheBox' , 'numberOfPassRushers', 'typeDropback', 'offenseFormation']]
    temp = pd.get_dummies(mod, prefix='offForm', columns = ['offenseFormation'])
    modPlays = pd.get_dummies(temp, prefix='typeDrop', columns = ['typeDropback'])
    modPlays.to_pickle(modPicklePath)

plays = modPlays

def closest_player(node, nodes):
    nodes = np.asarray(nodes)
    deltas = nodes - node
    dist_2 = np.einsum('ij,ij->i', deltas, deltas)
    #print(np.argmin(dist_2))
    return np.argmin(dist_2)

scaler = MinMaxScaler(feature_range=(0, 1))


def get_player_stats(nflId):
    statsArray = playersData[playersData['nflId'] == nflId]
    statsArray = statsArray[['height', 'weight']]
    #print(statsArray.to_numpy)
    return statsArray.values.tolist()

def get_play_stats(playId, gameId):
    statsArray = plays[(plays['playId'] == playId) & (plays['gameId'] == gameId)]
    statsTrim = statsArray.drop(['gameId', 'playId', 'offensePlayResult'], axis=1)
    return statsTrim.values.tolist()

def isolatePlay(week, gameNum, playNum, dropList):
    d = week[week['gameId'] == gameNum]
    t = d[d['playId'] == playNum]
    finalized_array=[]
    for  player in t.itertuples(index = True):
        
        if(player.team_football == 1):

            element = np.append(player, [-1, -1])
            element = np.append(element, [0, 0])
        

        else:

            p = [player.x, player.y] #new list with x,y of player
            ps = t[(t['team_away'] == player.team_away) & (t['team_home'] == player.team_home) & (t['frameId'] == player.frameId)] #getting other players on team
            ps = ps.drop(player[0], axis = 0) # dropping selected player from team
            ps =  ps[["x", "y"]]
            element = np.append(player, closest_player(p, ps))

            ps = t[(t['team_home'] == player.team_away) & (t['team_away'] == player.team_home) & (t['frameId'] == player.frameId)] #getting other players on opp. team
            ps =  ps[["x", "y"]]
            element = np.append(element, closest_player(p, ps))
            element = np.append(element, get_player_stats(player.nflId))

        element = np.append(element, get_play_stats(playNum, gameNum))
        trimmed = element[5:]
        varIndexs = list(range(0,63))
        keepIndexs = [elem for elem in varIndexs if elem not in dropList ]
        finalized_array.append(trimmed[keepIndexs])
        # print(len(finalized_array[0]))

            
    # print("Loop:",loop)
    # print("game:", gameNum)
    # print("play:", playNum)
    # print("finalized_array:\n",len(finalized_array))
    norm = scaler.fit_transform(finalized_array)
    
    return norm

def evaluate_model(model, modelName, train_x, test_x):
    # Final evaluation of the model
    trainPredict = model.predict(train_x)
    testPredict = model.predict(test_x)
    # invert predictions
    scaler.fit(trainPredict)
    denormTrainPredict = scaler.inverse_transform(trainPredict)
    denormTrainY = train_y * 100
    denormTestPredict = scaler.inverse_transform(testPredict)
    denormTestY = test_y * 100
    # calculate root mean squared error
    trainScore = math.sqrt(mean_squared_error(denormTrainY, denormTrainPredict[:,0]))

    print("Evaluating: ", modelName)
    print('Train Score: %.2f RMSE' % (trainScore))
    testScore = math.sqrt(mean_squared_error(denormTestY, denormTestPredict[:,0]))
    print('Test Score: %.2f RMSE' % (testScore))
    print("_______________________________________")
    return trainScore, testScore


print("creating ML training, test, and validation datasets")
first = True


def get_train_data(dropList, dropStr):
    matfile = '63varTrainData.mat'
    try:
        matdata = scipy.io.loadmat(matfile)
        x = matdata['x']
        y = matdata['y']
    except (FileNotFoundError) as e:
        print("creating train data...")
        first = True
        for rows in plays.itertuples():
            #print(getattr(rows, 'gameId'), gameMax)

            gameId =  getattr(rows, 'gameId')

            playId = getattr(rows, 'playId')
            d = week[week['gameId'] == gameId]
            t = d[d['playId'] == playId]
            if(len(t)!= 0):
                play = isolatePlay(week, gameId, playId, dropList)
                if (first):

                    x = [play]
                    y = [[getattr(rows, 'offensePlayResult')/100]]
                    first = False
                else:

                    x.append(play)
                    y.append([getattr(rows, 'offensePlayResult')/100])


        # normalize the dataset
        num_vars = len(x[0][0])
        print("num inputs to model:",num_vars)
        x =  sequence.pad_sequences(x, pad_length)  # pad sequences with 0's to make them all have fixed size of 1000

        x.reshape(len(x), pad_length, num_vars)
        x = x.astype(np.float32)



        # Write the array to the mat file. the arrays correspond to a key name of 'x' & 'y'
        scipy.io.savemat(matfile, mdict={'x': np.array(x), 'y': np.array(y)}, oned_as='row')

        # check if the data is the same
        matdata = scipy.io.loadmat(matfile)
        assert np.all(np.array(x) == matdata['x'])
        assert np.all(np.array(y) == matdata['y'])

    varIndexs = list(range(0,63))
    keepIndexs = [elem for elem in varIndexs if elem not in dropList ]

    modX = []
    for frame in x:
        modX.append(np.delete(frame, dropList, axis = 1 ))
        
    print(len(modX[0][0]))
    return modX, y




def create_model(lstmHiddenNodes, denseNodes, numLSTM, numDense, train_x, train_y, val_x, val_y):
    activation = 'sigmoid'
    loss = 'mse'
    batch_size = 128
    epochs = 10
    num_vars = len(train_x[0][0])

    modelPath = str(numLSTM) + 'x-lstm-hn'+ str(lstmHiddenNodes)+'-'+ str(numDense) +'x-dense-'+ str(denseNodes) +'-'+ activation +'-'+ loss +'_'+ str(num_vars) +'Vars_'+ str(batch_size) +'_ep' + str(epochs) +'.h5'
    try:

        model = load_model(modelPath)
        print("Model "+ modelPath +" loaded from file\n") 

    except(ImportError, IOError) as e:
        print("Load model " + modelPath + " failed")
        model = Sequential()
        for i in range(numLSTM):
            if(numLSTM - i == 1):
                model.add(LSTM(lstmHiddenNodes))
            else:
                 model.add(LSTM(lstmHiddenNodes, return_sequences=True))

        for i in range(numDense):
            model.add(Dense(denseNodes, activation=activation))
        model.compile(loss=loss, optimizer='adam', metrics=['mean_squared_error'])
        model.fit(train_x, train_y, validation_data=(val_x, val_y), epochs=epochs, batch_size=batch_size)
        print(model.summary())
        #model.save(modelPath)
    return model, modelPath

lstmHiddenNodes = 6
denseNodes = 6
numLSTM = 1
numDense = 2
loop = list(range(1,17))
with open(workDirectory + 'model_remove_input_test','w') as f1:
    writer=csv.writer(f1, delimiter=',',lineterminator='\n',)

    print("Begginning Input Analysis...")

    dropList = [] 
    dropStr = 'none'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])

    
    dropList = [0] 
    dropStr = 'x'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])
    
    dropList = [1] 
    dropStr = 'y'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])
    
    dropList = [1, 0] 
    dropStr = 'xy'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])
    
    dropList = [6,5] 
    dropStr = 'o and dir'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])

    dropList = [40, 39, 38] 
    dropStr = 'team'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])

    dropList = sorted(list(range(50, 57)), reverse=True) #indices for offensive formation dummy vars
    dropStr = 'offensiveFormations'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])    

    dropList = sorted(list(range(0, 7)), reverse=True)
    dropStr = 'trackingData'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])

    dropList = sorted(list(range(7, 20)), reverse=True)
    dropStr = 'playerRoute'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])

    dropList = sorted(list(range(20, 38)), reverse=True)
    dropStr = 'playerPosition'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])

    dropList = sorted(list(range(41, 42)), reverse=True)
    dropStr = 'closestTeammate'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])
    
    dropList = sorted(list(range(57, 64)), reverse=True)
    dropStr = 'typeDrop'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])

    dropList = sorted(list(range(48, 49)), reverse=True)
    dropStr = 'defendersInTheBox'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])

    dropList = sorted(list(range(49, 50)), reverse=True)
    dropStr = 'numberOfPassRushers'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])

    dropList = sorted(list(range(45, 46)), reverse=True)
    dropStr = 'down'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])
    
    dropList = sorted(list(range(0, 64)), reverse=True)
    dropStr = 'all'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])


    dropList = []
    dropStr = 'none'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])

    dropList = sorted(list(range(44, 45)), reverse=True)
    dropStr = 'weight'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])

    dropList = sorted(list(range(47, 48)), reverse=True)
    dropStr = 'yardline'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])
    dropList = sorted(list(range(40, 41)), reverse=True)
    dropStr = 'closestTeammate'
    xD, yD = get_train_data(dropList, dropStr)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)
    for x in loop:
        
        
        model, modelPath = create_model(lstmHiddenNodes, denseNodes,  numLSTM, numDense, train_x, train_y, val_x, val_y)
        trainMSE, testMSE = evaluate_model(model, modelPath, train_x, test_x) 
        writer.writerow([str(x), dropStr, str(trainMSE), str(testMSE)])