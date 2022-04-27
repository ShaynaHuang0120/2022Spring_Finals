# Data Analysis of Formula One Racing Strategy
IS 597 Final Project, 2022 Spring 

Group Members:
1. Andrew Mo(andrewmo1002)
2. Tianci Zheng(DylanZheng)
3. Ching-Yun Huang(ShaynaHuang0120)

Project Type: Type 1

### Contents

New General Research Topic:
- What are factors that influence the F1 Racing rank?
  - Car constructors
  - the time/speed for each lap 
  - Pit stop 

1. Pit Stop Strategies
   1. Hypothesis: Fewer pit stops give the driver a better rank in each race 
   2. Hypothesis: The pit stops are evenly distributed 
   3. Hypothesis: Evenly distributed pit stops give better race results

## 1. Pit Stop Strategies

### 1.1 Hypothesis: Fewer pit stops give the driver a better rank in each race

### 1.2 Hypothesis: The pit stops are evenly distributed through time

If we look at the distribution of the lap proportions of the pit stops, we can notice there seems to be a pattern. Here are what they look like in histograms.

![](https://i.imgur.com/WsPxIa7.png)
![](https://i.imgur.com/B3pgzDE.png)
![](https://i.imgur.com/ZVhOevG.png)

As shown, for each number of pit stops a team chose for the entire race, there appears to be a pattern in when they chose to pit. If the team chooses to pit only once in the entire race, they usually pit at the half of the race. If the team chooses to pit twice, they usually pit when it's near 1/3 and 2/3 of the total laps. The case is similar if they choose to pit thrice. 

Noticing this pattern, we came up with the second hypothesis that the pit stops are evenly distributed through time. Our null hypothesis is that all pits are normally distributed around the points the evenly dividing points (1/2, 1/3, 2/3, etc). 

To study such a pattern, we calculated the proportion of the total laps the driver pit at for each record in the racing results. For convenience, we call this proportion 'Lap Proportion'.
Before we start, there is one property of the Lap Proportion column that we should notice. The numeric range of the Lap Proportion is not ideally continuous. The range of values the Lap Proportion can take is actually a discrete set because the domains of values that the numerators and the denominators (i.e. laps and total laps) can only be chosen from two very limited sets. Due to the discrete nature of the data, the Lap Proportion data, grouped by any number of total pit stops, is not normally distributed by strict definition. 

However, the distribution statistics of these groups resemble the characteristics of normal distributions very well: All the data groups are distributed symmetrically around the mean, with around 68% falling within one standard deviation, and with around 95% falling within two standard deviations. It would also be intuitive that such a distribution would follow a distribution similar to the normal distribution. Hence, we only assume that pit stop time points of each group are normally distributed given a broader definition. 

Assuming these groups of data are normally distributed, we notice that the means deviate quite a bit from the ideal dividing points (1/2, 1/3, 2/3, etc.). Using one sample T-Tests, we calculated the p values for each group, and the results show that all the p values are significantly lower than the significant level of 0.05, with differences of at least 20 orders of magnitude.

In conclusion, we reject the null hypothesis and determine that the time points of the pit-stopping are not evenly distributed.


### 1.3 Hypothesis: Evenly distributed pit stops give better race results

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

From the histogram plots above, we can tell that the pit distributions of the higher-ranking results are more evenly distributed across the entire race than the lower-ranking results.  The differences are also statistically significant given the significance level of 0.05 for some of the pit stop order, including the first pit of total 2 pit stops and the all three pits of the total 3 pit stops.

![](https://i.imgur.com/Zez7YAu.png)
![](https://i.imgur.com/7HwUJ4s.png)
![](https://i.imgur.com/kuesDYy.png)

We can use an alternative view of the data to measure the deviation, by using the average deviations of how far the lap proportions of all pit records from each driver from each race are away from the evenly divided points. In this way, we can treat the pit distributing strategy of each race as a whole factor to measure how the driver performed in that race.

Similarly, we compare the results of higher ranking drivers with the lower ranking drivers and test them with the non-parametric Mann-Whitney U tests, with resulting p-values ranging from 0.002 to 0.022, meaning that all of the tests are significant against the 0.05 significance level.

Thus, we concluded that we accept the null hypothesis that the evenly distributed pit stops give better racing results.
 
## 2. Racing Speed Strategy

## 3. Result Summary and Conclusions














