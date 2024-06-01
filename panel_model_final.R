### LOAD LIBRARIES
library(plm)
library(dplyr)
library(lubridate)
library(foreign)
library(modelsummary)
library(car)

rm(list=ls())

### LOAD DATA
data = read.csv("aggregation_attempt.csv")
data_nocovid <- data %>% subset(Month < "2020-04")

borough_list <- data %>% subset(select=c(Borough.name_x, Borough.name_y, Borough.name))

data_useful_t <- data %>% subset(select=c(Month, Ward.name, qLivedInAreaForYears, qWorriedAboutCrimeInArea, 
                                                qGoodJobLocal, qGoodJobLondon,qReliedOnToBeThere, qTreatEveryoneFairly, qDealWithWhatMattersToTheCommunity,
                                                qConfidentThatStopAndSearchFair, qInformedLocal, qInformedLondon, Trust, qPoliceHeldAccountable, crimeTheft, 
                                                crimeViolence, crimePublicDisorder, resolutionYes, Pay, jobDensity, Female, Other,
                                                X10.17, X18.24, X25.34, over.34, Asian, Black, Other.1, searchReasonCriminal, searchReasonDrugs, outcomeUnsuitableForSearch))


data_useful_nocovid_t <- data_nocovid %>% subset(select=c(Month, Ward.name, qLivedInAreaForYears, qWorriedAboutCrimeInArea, 
                                                        qGoodJobLocal, qGoodJobLondon,qReliedOnToBeThere, qTreatEveryoneFairly, qDealWithWhatMattersToTheCommunity,
                                                        qConfidentThatStopAndSearchFair, qInformedLocal, qInformedLondon, Trust, qPoliceHeldAccountable, crimeTheft, 
                                                        crimeViolence, crimePublicDisorder, resolutionYes, Pay, jobDensity, Female, Other,
                                                        X10.17, X18.24, X25.34, over.34, Asian, Black, Other.1, searchReasonCriminal, searchReasonDrugs, outcomeUnsuitableForSearch))

data_useful_c <- data %>% subset(select=c(Month, Ward.name, qLivedInAreaForYears, qWorriedAboutCrimeInArea, 
                                          qGoodJobLocal, qGoodJobLondon,qReliedOnToBeThere, qTreatEveryoneFairly, qDealWithWhatMattersToTheCommunity,
                                          qConfidentThatStopAndSearchFair, qInformedLocal, qInformedLondon, Trust, Confidence, qPoliceHeldAccountable, crimeTheft, 
                                          crimeViolence, crimePublicDisorder, resolutionYes, Pay, jobDensity, Female, Other,
                                          X10.17, X18.24, X25.34, over.34, Asian, Black, Other.1, searchReasonCriminal, searchReasonDrugs, outcomeUnsuitableForSearch))

data_useful_nocovid_c <- data_nocovid %>% subset(select=c(Month, Ward.name, qLivedInAreaForYears, qWorriedAboutCrimeInArea, 
                                                  qGoodJobLocal, qGoodJobLondon,qReliedOnToBeThere, qTreatEveryoneFairly, qDealWithWhatMattersToTheCommunity,
                                                  qConfidentThatStopAndSearchFair, qInformedLocal, qInformedLondon, Trust, Confidence, qPoliceHeldAccountable, crimeTheft, 
                                                  crimeViolence, crimePublicDisorder, resolutionYes, Pay, jobDensity, Female, Other,
                                                  X10.17, X18.24, X25.34, over.34, Asian, Black, Other.1, searchReasonCriminal, searchReasonDrugs, outcomeUnsuitableForSearch))

pdata_t <- pdata.frame(data_useful_t[, c(2,1,3:ncol(data_useful_t))])
pdata_nocovid_t <- pdata.frame(data_useful_nocovid_t[, c(2,1,3:ncol(data_useful_nocovid_t))])
pdata_c <- pdata.frame(data_useful_c[, c(2,1,3:ncol(data_useful_c))])
pdata_nocovid_c <- pdata.frame(data_useful_nocovid_c[, c(2,1,3:ncol(data_useful_nocovid_c))])

### DEFINE FORMULAS 
remove_t <- c("Trust", "Month", "Ward.name")
remove_c <- c("Confidence","Month", "Ward.name")
formula_trust <- as.formula(paste("Trust ~", paste(setdiff(colnames(data_useful_t), remove_t), collapse= " + ")))
formula_confidence <- as.formula(paste("Confidence ~", paste(setdiff(colnames(data_useful_c), remove_c), collapse= " + ")))
formula_confidence

### TEST FOR MULTICOLLINEARITY
testmodel <- lm(Trust ~ ., data=data_useful_t)
ld.vars <- attributes(alias(testmodel)$Complete)$dimnames[[1]]
ld.vars
vif(testmodel)
testmodel
# resolutionNo, crimeOther, Male, under.10, White. searchReasonFirearms, 
# outcomeSuitableForSearch all dropped from the above df's due to 
# high multicollinearity

### PERFORM STATISTICAL TESTS TOO CHOOSE A SUITABLE MODEL

# F_test_fixed <- function(data_useful){ # F-test for fixed effect
#   pooled <- lm(Trust ~ .-Month -Ward.name, data=data_useful)
#   R2_pooled <- summary(pooled)$r.squared 
#   
#   LSDV <- lm(Trust ~ ., data=data_useful)
#   R2_LSDC <- summary(LSDV)$r.squared 
#   
#   nT <- nrow(data_useful)
#   n <- length(unique(data_useful$Ward.name))
#   k <- ncol(data_useful) - 1
#   # print(nT)
#   # print(n)
#   # print(k)
#   
#   F_stat <- ((R2_LSDC - R2_pooled)/(n-1))/((1 - R2_LSDC)/(nT-n-k))
#   print(F_stat)
#   return(pf(F_stat, n-1, nT-n-k) <= 0.05)
# }
# fixed_result <- F_test_fixed(data_useful)
# fixed_result_nocovid <- F_test_fixed(data_useful_nocovid)



## Testing for presence of fixed individual (ward) and time effects

gp_t <- plm(formula_trust, data = pdata_t, model = "pooling")
gi_t <- plm(update(formula_trust, reformulate(c(".", "Ward.name"))), data = pdata_t, model = "pooling")
gt_t <- plm(update(formula_trust, reformulate(c(".", "Month"))), data = pdata_t, model = "pooling")
gd_t <- plm(update(formula_trust, reformulate(c(".", "Month + Ward.name"))), data = pdata_t, model = "pooling")


sprintf("Fixed individual effect in all data: %s", pFtest(gi_t, gp_t)$p.value <= 0.05)
sprintf("Fixed time effect in all data: %s", pFtest(gt_t, gp_t)$p.value <= 0.05)
sprintf("Fixed mixed effect in all data: %s", pFtest(gd_t, gp_t)$p.value <= 0.05)

# All data has both time and individual effects

gp_t_cov <- plm(formula_trust, data = pdata_nocovid_t, model = "pooling")
gi_t_cov <- plm(update(formula_trust, reformulate(c(".", "Ward.name"))), data = pdata_nocovid_t, model = "pooling")
gt_t_cov <- plm(update(formula_trust, reformulate(c(".", "Month"))), data = pdata_nocovid_t, model = "pooling")
gd_t_cov <- plm(update(formula_trust, reformulate(c(".", "Month + Ward.name"))), data = pdata_nocovid_t, model = "pooling")

sprintf("Fixed individual effect in non-covid data: %s", pFtest(gi_t_cov, gp_t_cov)$p.value <= 0.05)
sprintf("Fixed time effect in non-covid data: %s", pFtest(gt_t_cov, gp_t_cov)$p.value<= 0.05)
sprintf("Fixed mixed effect in non-covid data: %s", pFtest(gd_t_cov, gp_t_cov)$p.value<= 0.05)

# Non-covid data has only the time effect (and mixed effect too)

## Testing for presence of random individual (ward) and time effects (Breush-Pagan 1980)

sprintf("Random individual effect in all data: %s", plmtest(gp_t, type="bp", effect="individual")$p.value <= 0.05)
sprintf("Random time effect in all data: %s", plmtest(gp_t, type="bp", effect="time")$p.value<= 0.05)
sprintf("Random mixed effect in all data: %s", plmtest(gp_t, type="ghm", effect="twoways")$p.value<= 0.05) # ghm is only available for twoways, but robust for unbalanced panel

sprintf("Random individual effect in non-covid data: %s", plmtest(gp_t_cov, type="bp", effect="individual")$p.value <= 0.05)
sprintf("Random time effect in non-covid data: %s", plmtest(gp_t_cov, type="bp", effect="time")$p.value<= 0.05)
sprintf("Random mixed effect in non-covid data: %s", plmtest(gp_t_cov, type="ghm", effect="twoways")$p.value<= 0.05) # ghm is only available for twoways, but robust for unbalanced panel

# In both data cases, only time  (and mixed) random effect present 

## Testing which model is better (fixed effect vs random effect; mixed and time)

wi <- plm(formula_trust, data = pdata_t, model = "within", effect='twoways')
re <- plm(formula_trust, data = pdata_t, model = "random", effect='twoways')

wi_time <- plm(formula_trust, data = pdata_t, model = "within", effect='time')
re_time <- plm(formula_trust, data = pdata_t, model = "random", effect='time')

wi_cov <- plm(formula_trust, data = pdata_nocovid_t, model = "within", effect='twoways')
re_cov <- plm(formula_trust, data = pdata_nocovid_t, model = "random", effect='twoways')

wi_time_cov <- plm(formula_trust, data = pdata_nocovid_t, model = "within", effect='time')
re_time_cov <- plm(formula_trust, data = pdata_nocovid_t, model = "random", effect='time')

phtest(wi,re)
phtest(wi_time,re_time)
phtest(wi_cov, re_cov)
phtest(wi_time_cov, re_time_cov)

# Results signify that the time effects may be correlated with at least one of the regressors -> thus, we need to use the fixed-effect model
# Furthermore, we can use consider only the time effect in cases on non-covid data.


# Thus, the final best model specifications are: 
# - Fixed effect model with twoways effect using all data
# - Fixed effect model with time effect using non-covid data

### ANALYSIS

final_model_all <- wi
final_model_nocov <- wi_time_cov

summary(final_model_all)
summary(final_model_nocov)

simpler_final_all <- plm(Trust ~ qWorriedAboutCrimeInArea + qGoodJobLocal + 
                           qGoodJobLondon + qReliedOnToBeThere + 
                           qTreatEveryoneFairly + 
                           qDealWithWhatMattersToTheCommunity + 
                           qConfidentThatStopAndSearchFair + 
                           qInformedLondon + 
                           qPoliceHeldAccountable + 
                           Other + Asian + Black + Other.1 + outcomeUnsuitableForSearch, 
                         data = pdata_t, model = "within", effect='twoways')
simpler_final_nocov <- plm(Trust ~ qGoodJobLocal + qGoodJobLondon + 
                             qReliedOnToBeThere + qTreatEveryoneFairly + 
                             qDealWithWhatMattersToTheCommunity + 
                             qConfidentThatStopAndSearchFair + qInformedLondon + 
                             qPoliceHeldAccountable + crimePublicDisorder + 
                             resolutionYes + Asian + Black + Other.1 + 
                             outcomeUnsuitableForSearch, data = pdata_t, 
                           model = "within", effect='time')

summary(simpler_final_all)
summary(simpler_final_nocov)

### FURTHER ANALYSIS -> PUTTING MORE ATTENTION TO CERTAIN CATEGORIES


