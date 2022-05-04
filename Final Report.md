# Topic: Racing Strategies of Formula One

## Background
Formula 1 (a.k.a. F1 or Formula One) is one of the most popular car racing competitions, receiving lots of attention and participation from worldwide car manufacturers and players. Being the highest class of single-seater auto racing, F1 is sanctioned by the Fédération Internationale 
de l'Automobile (FIA) and is owned by the Formula One Group. 
One of the fascinating components in F1 is the pit stop in which the players stop the car to perform maintenance such as tire replacement and fuel refilling within seconds. Thus, how to wisely utilize pit stops has become one popular topic in F1. And the authors of the previous project and we decided to focus on the strategies of F1 like pit stops distribution and eventually the effect on the ranking.

## Relavent Term Definition
- Pit stop: The stop point for drivers to pull over and get their car maintenanced
- Lap time: The time for a car to run one round of the total laps


## Contents
1. Original Work Review
   1. Introduction
   2. Critique
   3. Improvement Description 
2. Data Analytics of Racing Strategies of Formula One
   1. Pit Stop Strategy
      1. Hypothesis: Fewer pit stops give the driver a better rank in each race 
      2. Hypothesis: The pit stops are evenly distributed 
      3. Hypothesis: Evenly distributed pit stops give better race results
   2. Racing Speed Strategy
      1. Hypothesis: 
   3. Exploratory Analysis on Car Constructors and Groups
   4. Results Summary


## 1. Original Work Review
### 1.1 Original Work Introduction
#### 1.1.1 Original Dataset
Data Source: https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020

The dataset include 14 csv files for all the relevant information of F1 racing including circuits, drivers, races, results, lap times, pit stops, qualifying, championships, and constructors.
#### 1.1.2 Original work Description
Original Work GitHub Link: https://github.com/ho-yi-shiuan/2021_Spring_finals

In their project, the authors analyzed the strategy of pit stops on race results of Formula One (F1). They proposed two hypotheses. The first one was "Less pit stops gives the driver better rank in each race."
And the second was Laps of each pit stop time should be similar for better tire usage.

In their first hypothesis, they created the boxplot and bar charts showing the distribution of positions based on the total number of pit stops.
They concluded that there was no strong relationship between pit stop counts and positions since the distribution did not change
the pit stop changed.

Second, they had several line charts showing the relationship between the proportion of total laps and race count. The results demonstrated that
most of the pit stop timing was average and thus stated that they didn't have strong evidence to reject the second hypothesis

### 1.2 Critique of The Original Work
#### 1.2.1 Hypotheses
Their results didn't align with their graphic for the first hypothesis, as distributions changed when the pit stop number varied. Potential patterns appeared in their bar charts which we will investigate more.
They also did not have any further substantial statistical methods to support their results further. 

The second hypothesis was very unclear and confusing in general. 
Through the analysis, there was no information regarding the tire usage. 
Also, they failed to analyze the time pattern in the different number of pit stops as we discovered that the proportions of total laps could have potential effects on the race results. This hypothesis was not consistent with their topic as well.

#### 1.2.2 Coding
We identified three major issues in their coding part. First, they had poor documentation since they missed end-user instruction, preventing any reviewer from understanding
their whole project and code quickly and easily. Their docstrings were also low-quality. Many were short sentences and did not clearly reveal the actual goals and steps.

The authors also included redundant and necessary functions, such as read_data and delete_data. They merely utilized built-in functions in Pandas library without any additional code to improve the functionality.

Moreover, the whole coding part had low modularity. In detail, their "main function" part had many lines of unorganized code, even a for loop to plot the charts. Such a hard-core style significantly reduced the reusability and lowered the efficiency.

### 1.3 Improvement Description

Our goals in this project includes two main parts and improvements:
- Analysis
  - Correct and improve existing hypotheses
  - Propose new hypotheses based on the existing dataset
  - Propose new topic and additional hypotheses on additional dataset & data source
  - Introduce statistical testing (Mann-Whitney U, T test)
  - Readme file
  

- Code Implementation
  - Comprehensive docstrings and doctests 
  - High Modularity and usability
  - Efficiency techniques 

  


## 2. Data Analytics of Racing Strategies of Formula One
### 2.1. Pit Stop Strategy

#### 2.1.1. Hypothesis: Fewer pit stops give the driver a better rank in each race

The following boxplot shows the distribution of position for drivers taking different number of pit stop. As we can see, drivers taking 1 pit stop usually get position around 7, and it goes up to around 9 and 10 for drivers taking more than 1 pit stop. 

![](https://imgur.com/rkg3PXE.png)

The results prove that the less the total pit stops take, the higher rank the drivers get. 
Since pit stops ranging from 1 to 3 have better interpretation of the correlation, we then focus on drivers taking 1, 2 or 3 pit stops to do the following detailed analysis. 
For drivers taking 1 pit stop, the distribution of rank concentrates on rank 1 to 10, and the concentrated distribution extends to 1 to 13 for drivers taking 2 pit stop.
However, when drivers take 3 pit stop, their ranks are mainly distributed from rank 10 to 15. The results prove the positive relationship between pit stop counts and positions.
    
![](https://imgur.com/5PZRGWr.png)

![](https://imgur.com/GHVgd9A.png) 

![](https://imgur.com/US8ivgu.png)

To strengthen the analysis result, we compare the rank distribution of drivers taking 1, 2 or 3 pit stops and test them with the non-parametric Mann-Whitney U tests.

![](https://imgur.com/He5EIhD.png)

The resulting p-values are range from 0.00000000000279 to 0.00008, meaning that all the tests are significant against the 0.05 significance level.
Thus, we reject the null hypothesis and determine the rank distributions between drivers taking 1, 2 or 3 total pit stops are significantly different.

In conclusion, we accept the hypothesis that fewer pit stops give the driver a better rank in each race.

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
#### 2.2.1. Hypothesis: Evenly distributed lap time gives better results

![](https://imgur.com/TRHlLGf.png)

H0: There is no significant difference in the distribution of lap times STD between the ranking of drivers.

![](https://imgur.com/PFJJ11l.png)
![](https://imgur.com/oTsj1JP.png)

...

### 2.3 Exploratory Analysis on Car Constructors and Groups

####2.3.1 Overview
In addition to our hypotheses on F-1 Racing strategies, we also utilize other available file in the F-1 dataset and other
data source to conduct some exploratory and descriptive analysis. In this case, we found that the car constructors and car groups
presents some interesting patterns and trends regarding the winning times.

#### 2.3.2 New Data Source
Formula E Championship from Season 1 to 7

Source: https://www.kaggle.com/datasets/mlandry/formula-e-championship

#### 2.3.3 Winning Frequency

We first plot the winning frequency in 

![](https://imgur.com/a/8y6mh2G.png)


...

### 2.4. Results Summary

#### 2.4.1. Pit Stop Strategy

According to the results of the hypothesis tests under the topic of pit-stopping, we learn that we accept all the null hypotheses except the second one. 

We learned that the strategy of having fewer pit stops appears to have a positive effect on giving the driver a better rank in races. We suspect the reason behind this phenomenon is that the drivers who choose to pit fewer tend to have confidence in their equipment so that they think only one pit or two could be enough for the entire race. Conversely, their confidence could be from the quality and stability of their equipment, and, thus, the quality and stability lower the chances of accidents or equipment malfunctions. 

We learned that the pit stops are not ideally evenly distributed throughout the races. Instead, it seems that the drivers tend to pit before arriving at the evenly dividing points. Such a shift in the distribution could be accounted for that the drivers will follow their pit-stopping plans and usually will only pit in advance when they think something goes wrong.

We learned that the drivers who distribute the lap proportions of their pit stops evenly tend to have better race results. The better usage of equipment (tires, gasoline, ...) could be part of the contributing factor of such a phenomenon.

















