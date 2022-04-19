# Data Analysis of Formula One Racing Strategy
IS 597 Final Project, 2022 Spring 

Group Members:
1. Andrew Mo(andrewmo1002)
2. Tianci Zheng(DylanZheng)
3. Ching-Yun Huang(ShaynaHuang0120)

Project Type: Type 1

### Contents
1. Pit Stop Strategies
   1. Hypothesis: Fewer pit stops give the driver a better rank in each race 
   2. Hypothesis: The pit stops are evenly distributed 
   3. Hypothesis: Evenly distributed pit stops give better race results

## 1. Pit Stop Strategies

### 1.1 Hypothesis: Fewer pit stops give the driver a better rank in each race

### 1.2 Hypothesis: The pit stops are evenly distributed

![](https://i.imgur.com/1aBZcI1.png)

As shown, for each number of pit stops a team chose for the entire race, there appears to be a pattern in when they chose to pit stop. 

If the team chooses to pit stop only once in the entire race, they usually pit during the half of the race. If they choose to pit stop twice, they usually pit when it's near 1/3 and 2/3 of the total laps. The case is similar if they choose to pit thrice. 

Due to the discrete nature of the data, the normality tests are not applicable here and, thus, all data groups are not normally distributed by strict definition. 
However, the histograms appear that the data groups are normally distributed, and actually, the statistical characteristics of the frequency distribution indeed resemble the characteristics of normal distributions: All of the data groups are distributed symmetrically around the mean, around 68% fall within one standard deviation, and around 95% fall within two standard deviations. Hence, we assume that pit stop time points of each group are normally distributed given a broader definition. 

Under such assumption and given a significance level of alpha = 0.05, we used T-tests on the groups of time points in different combinations, resulting in p-values all under 0.05, and thus we accept that each group of time points follows a distinct distribution.

Learning the distribution of each group of time points follows and given the fact that the means of each group are around the evenly dividing points (1/2, 1/3, 2/3, 1/4, ...) for all 3 kinds of the total number of pit stops, we determine that the time points of the pit-stopping are evenly distributed.


### 1.3 Hypothesis: Evenly distributed pit stops give better race results














