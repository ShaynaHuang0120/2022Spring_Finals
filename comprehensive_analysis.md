#Topic: Racing Strategies of Formula One

##Background
Cited from
"Formula 1 (a.k.a. F1 or Formula One) is the highest class of single-seater auto racing sanctioned by the Fédération Internationale de l'Automobile (FIA) and owned by the Formula One Group. The FIA Formula One World Championship has been one of the premier forms of racing around the world since its inaugural season in 1950. The word "formula" in the name refers to the set of rules to which all participants' cars must conform. A Formula One season consists of a series of races, known as Grands Prix, which take place worldwide on purpose-built circuits and on public roads."

## Contents
1. Original Work Review
   1. Introduction
   2. Critique
   3. Improvements 
2. Data Analysis
   1. Pit Stop Strategy
      1. Hypothesis: Fewer pit stops give the driver a better rank in each race 
      2. Hypothesis: The pit stops are evenly distributed 
      3. Hypothesis: Evenly distributed pit stops give better race results
   2. Racing Speed Strategy
      1. Hypothesis: 
   3. Other Topics
   4. Results Summary
      1. Pit Stop Strategy
      2. Racing Speed Strategy
      3. Other Topics

## 1. Original Work Review
### 1.1 Original Work Introduction
#### 1.1.1 Original Dataset
Data Source: https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020

The dataset include 14 csv files for all the relevant information of F1 racing including cir
#### 1.1.2 Original work







## 2. Data Analysis
### 2.1. Pit Stop Strategy

...

#### 2.1.1. Hypothesis: Fewer pit stops give the driver a better rank in each race

#### 2.1.2. Hypothesis: The pit stops are evenly distributed through time

Before we move on to the next hypothesis, let us introduce the concept we call 'Lap Proportion'. Lap proportion represents where or when the driver pit in a race, which we measure by dividing the number of laps the driver has already finished (*pit lap) by the total laps required to finish for that race.

![](https://i.imgur.com/mxcMgDn.png)

If we look at the distribution of the lap proportions of all the pit stop records, we can notice there seems to be a pattern. Here are what they look like in histograms.

![](https://i.imgur.com/WsPxIa7.png)
![](https://i.imgur.com/B3pgzDE.png)
![](https://i.imgur.com/ZVhOevG.png)

As shown, for each number of pit stops a team chose for the entire race, there appears to be a pattern in when they chose to pit. If the team chooses to pit only once in the entire race, they usually pit at the half of the race. If the team chooses to pit twice, they usually pit when it's near 1/3 and 2/3 of the total laps. The case is similar if they choose to pit thrice. 

Noticing this pattern, we came up with the second hypothesis that the pit stops are evenly distributed through time. Our null hypothesis is that all pits are normally distributed around the points the evenly dividing points (1/2, 1/3, 2/3, etc). 

To study such a pattern, we calculated the Lap Proportions for each record in the racing results.
There is one property of the Lap Proportion column that we should notice. The numeric range of the Lap Proportion is not ideally continuous. The range of values the Lap Proportion can take is actually a discrete set because the domains of values that the numerators and the denominators (i.e. laps and total laps) can only be chosen from two very limited sets. Due to the discrete nature of the data, the Lap Proportion data, grouped by any number of total pit stops, is not normally distributed by strict definition. 

However, the distribution statistics of these groups resemble the characteristics of normal distributions very well: All the data groups are distributed symmetrically around the mean, with around 68% falling within one standard deviation, and with around 95% falling within two standard deviations. It would also be intuitive that such a distribution would follow a distribution similar to the normal distribution. Hence, we only assume that pit stop time points of each group are normally distributed given a broader definition. 

Here are the statistics and p values we calculated for each data group. 
![](https://i.imgur.com/GdxCG8P.png)
![](https://i.imgur.com/RTMAeDZ.png)
![](https://i.imgur.com/nhYVxf0.png)

Assuming these groups of data are normally distributed, we notice that the means deviate quite a bit from the ideal dividing points (1/2, 1/3, 2/3, etc.). Using one sample T-Tests, we calculated the p values for each group, and the results show that all the p values are significantly lower than the significant level of 0.05, with differences of at least 20 orders of magnitude.

If we exclude the normality assumption, and use Wilcoxon signed-rank tests, the one sample non-parametric mean comparison test, instead, we will get similar results, with the p values at least 20 orders of magnitude smaller.

In conclusion, we reject the null hypothesis and determine that the time points of the pit-stopping are not evenly distributed.


#### 2.1.3. Hypothesis: Evenly distributed pit stops give better race results

To learn about the differences in the distributions of the pit stops of different position rankings, we first divide the dataset into two categories: high ranking and low ranking. The high ranking data are those with position order higher than 6, while the low ranking data are the rest, i.e. all the data below rank 5. To balance the cardinality of the two dataset, we resample the lower ranking data to the size of the high ranking data. And then, we plot them with histograms like we did for the Hypothesis 2, and here are what we got.

#### Total Pit Stop = 1
##### no. 1 pit stop
![](https://i.imgur.com/uPzYobQ.png)
#### Total Pit Stop = 2
##### no. 1 pit stop
![](https://i.imgur.com/VLSGqcK.png)
##### no. 2 pit stop
![](https://i.imgur.com/4IRprQS.png)
#### Total Pit Stop = 3
##### no. 1 pit stop
![](https://i.imgur.com/9wuGEoW.png)
##### no. 2 pit stop
![](https://i.imgur.com/S6mo1UB.png)
##### no. 3 pit stop
![](https://i.imgur.com/rwT1js2.png)

From the histogram plots above, we can tell that the Lap Proportion distributions of the higher-ranking results are more evenly distributed across the entire race than the lower-ranking results. 

The differences are statistically significant given the significance level of 0.05 for some pit stop order, including the first pit of total 2 pit stops and the all three pits of the total 3 pit stops. Here are the statistics for each data group.

![](https://i.imgur.com/EiEiMJ1.png)

We can use an alternative view of the data to measure the deviation, by using the average deviations of how far the lap proportions of all pit records from each driver from each race are away from the evenly dividing points. 

![](https://i.imgur.com/S2IoesM.png)

In this way, we can treat the pit distributing strategy of each race as a whole factor to measure how the driver performed in that race.

![](https://i.imgur.com/Zez7YAu.png)
![](https://i.imgur.com/7HwUJ4s.png)
![](https://i.imgur.com/kuesDYy.png)

Similarly, we compare the results of higher ranking drivers with the lower ranking drivers and test them with the non-parametric Mann-Whitney U tests, with resulting p-values ranging from 0.002 to 0.022, meaning that all of the tests are significant against the 0.05 significance level.

![](https://i.imgur.com/Y91I5E2.png)

Thus, we concluded that we accept the null hypothesis that the evenly distributed pit stops give better racing results.
 
### 2.2. Racing Speed Strategy

...

### 2.3. Other Topics

...

### 2.4. Results Summary

#### 2.4.1. Pit Stop Strategy

According to the results of the hypothesis tests under the topic of pit-stopping, we learn that we accept all the null hypotheses except the second one. 

We learned that the strategy of having fewer pit stops appears to have a positive effect on giving the driver a better rank in races. We suspect the reason behind this phenomenon is that the drivers who choose to pit fewer tend to have confidence in their equipment so that they think only one pit or two could be enough for the entire race. Conversely, their confidence could be from the quality and stability of their equipment, and, thus, the quality and stability lower the chances of accidents or equipment malfunctions. 

We learned that the pit stops are not ideally evenly distributed throughout the races. Instead, it seems that the drivers tend to pit before arriving at the evenly dividing points. Such a shift in the distribution could be accounted for that the drivers will follow their pit-stopping plans and usually will only pit in advance when they think something goes wrong.

We learned that the drivers who distribute the lap proportions of their pit stops evenly tend to have better race results. The better usage of equipment (tires, gasoline, ...) could be part of the contributing factor of such a phenomenon.

















