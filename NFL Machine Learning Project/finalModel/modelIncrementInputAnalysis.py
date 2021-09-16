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
import random
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

def get_random_list(arrSize):
    randomArr = np.random.rand(1,arrSize)
    return randomArr

def isolatePlay(week, gameNum, playNum, modInputs):
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
        for i in modInputs:
            trimmed[i] = random.random()
        finalized_array.append(trimmed)
        # print(len(finalized_array[0]))

            
    # print("Loop:",loop)
    # print("game:", gameNum)
    # print("play:", playNum)
    # print("finalized_array:\n",len(finalized_array))
    norm = scaler.fit_transform(finalized_array)
    
    return norm

def evaluate_model(model, modelName, train_x, test_x, train_y, test_y):
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

    # print("Evaluating: ", modelName)
    # print('Train Score: %.2f RMSE' % (trainScore))
    testScore = math.sqrt(mean_squared_error(denormTestY, denormTestPredict[:,0]))
    # print('Test Score: %.2f RMSE' % (testScore))
    # print("_______________________________________")
    return trainScore, testScore

def evaluate_increment_inputs_model(model, test_x, test_y, modInputs, increment, inputStr):
    testPredict = model.predict(test_x) * 100
    denormTestY = test_y * 100
    testValues = list(range(0,increment))
    with open('model_increment_input_exp.csv','a') as f1:
        writer=csv.writer(f1, delimiter=',',lineterminator='\n',)
        writer.writerow(testPredict[:,0])
        for testVal in testValues:
            for n in range(0, test_x.shape[0]):
                for i in modInputs:
                    for k in range(0, test_x[n][i].size):
                        test_x[n][i][k] = testVal/increment
            
            testResult = model.predict(test_x) * 100
            print(testVal/increment)
            writer.writerow([inputStr, str(testVal/increment)] + testResult[:,0])

    print("Input Increment Analysis finished. Results: model_increment_input_exp.csv")

def evaluate_dummy_inputs_model(model, test_x, test_y, modInputs, inputStr):
    testPredict = model.predict(test_x) * 100
    denormTestY = test_y * 100
    testValues = list(range(0,1))
    with open('model_dummy_input_exp.csv','a') as f1:
        writer=csv.writer(f1, delimiter=',',lineterminator='\n',)
        writer.writerow(testPredict[:,0])

        for n in range(0, test_x.shape[0]):
            for i in modInputs:
                for k in range(0, test_x[n][i].size):
                    for j in modInputs:
                        test_x[n][j][k] = 0
                    test_x[n][i][k] = 1
            
                testResult = model.predict(test_x) * 100
                writer.writerow([inputStr, str(i)] + list(str(testResult[:,0])))

    print("Dummy Input Analysis finished. Results: model_increment_input_exp.csv")



print("creating ML training, test, and validation datasets")
first = True


def get_train_data(matfile):
    try:
        print("loading...", matfile)
        matdata = scipy.io.loadmat(matfile)
        x = matdata['x']
        y = matdata['y']
    except (FileNotFoundError) as e:
      print("mat file error")

    # for n in range(0, x.shape[0]):
    #     for i in modInputs:
    #         for k in range(0, x[n][i].size):
    #             x[n][i][k] = random.random()
    
    return x, y


def load_existing_model(modelPath):
    model = load_model(modelPath)
    print("Model "+ modelPath +" loaded from file\n")
    return model

# adjusting input values systematically to compare the new prediction for the play
lstmHiddenNodes = 6
denseNodes = 6
numLSTM = 1
numDense = 2


with open('model_rand_input_exp.csv','w') as f1:
    writer=csv.writer(f1, delimiter=',',lineterminator='\n',)

    print("Begginning Input Analysis...")
    modelPath = workDirectory + '1x-lstm-hn6-2x-dense-6-sigmoid-mse_64Vars_128_ep100.h5'
    model = load_existing_model(modelPath)
    matfile = workDirectory + 'week_2_5_7_9_64varTrainData.mat'

    xD, yD = get_train_data(matfile)
    train_x, test_x, train_y, test_y = train_test_split(np.array(xD), np.array(yD), test_size=0.3)
    test_x, val_x, test_y, val_y = train_test_split(test_x, test_y, test_size=0.5)

    ################################################################
    ################################################################

    modInputs = sorted(list(range(49, 57)), reverse=True) #indices for offensive formation dummy vars
    inputStr = 'Offensive Formation'
    increment = 1
    evaluate_dummy_inputs_model(model, test_x, test_y, modInputs, inputStr)

    modInputs = sorted(list(range(57, 64)), reverse=True) #indices for offensive formation dummy vars
    inputStr = 'Type Dropback'
    increment = 1
    evaluate_dummy_inputs_model(model, test_x, test_y, modInputs, inputStr)

    ################################################################
    ################################################################


    modInputs = sorted(list(range(7, 20)), reverse=True)
    inputStr = 'Player Route'
    increment = 1
    evaluate_dummy_inputs_model(model, test_x, test_y, modInputs, inputStr)

    modInputs = sorted(list(range(20, 38)), reverse=True)
    inputStr = 'Player Position'
    evaluate_dummy_inputs_model(model, test_x, test_y, modInputs, inputStr)


    modInputs = sorted(list(range(41, 42)), reverse=True)
    inputStr = 'Closest Teammate'
    increment = 100
    evaluate_increment_inputs_model(model, test_x, test_y, modInputs, increment, inputStr)

    modInputs = sorted(list(range(42, 43)), reverse=True)
    inputStr = 'Closest Opponent'
    evaluate_increment_inputs_model(model, test_x, test_y, modInputs, increment, inputStr)

    
    modInputs = [45]
    inputStr = 'Down'
    increment = 4
    evaluate_increment_inputs_model(model, test_x, test_y, modInputs, increment, inputStr)

    modInputs = [45]
    inputStr = 'Yards To Go'
    increment = 100
    evaluate_increment_inputs_model(model, test_x, test_y, modInputs, increment, inputStr)

    modInputs = [47]
    inputStr = 'Yardline'
    increment = 100
    evaluate_increment_inputs_model(model, test_x, test_y, modInputs, increment, inputStr)

    modInputs = [48]
    inputStr = 'Defenders In The Box'
    increment = 10
    evaluate_increment_inputs_model(model, test_x, test_y, modInputs, increment, inputStr)

    modInputs = [49]
    inputStr = 'Number of Pass Rushers'
    increment = 10
    evaluate_increment_inputs_model(model, test_x, test_y, modInputs, increment, inputStr)

    modInputs = [43]
    inputStr = 'Height'
    increment = 100
    evaluate_increment_inputs_model(model, test_x, test_y, modInputs, increment, inputStr)

    modInputs = [44]
    inputStr = 'Weight'
    increment = 500
    evaluate_increment_inputs_model(model, test_x, test_y, modInputs, increment, inputStr)
