### LOAD LIBRARIES
library(plm)
library(dplyr)
library(lubridate)
library(foreign)
library(modelsummary)
library(car)
library(Hmisc)

rm(list=ls())
set.seed(10294)

### LOAD DATA
data = read.csv("C:/Users/hetvi/Downloads/all_joined_month_ward.csv")

data$logPay <- log(data$Pay)
data$logjobDensity<- log(data$jobDensity)
data_nocovid <- data %>% subset(Month < "2020-04")

borough_list <- data %>% subset(select=c(Borough.name_x, Borough.name_y, Borough.name))

data_useful_c <- data %>% subset(select=c(Month, Ward.name, qLivedInAreaForYears, qWorriedAboutCrimeInArea, qConfidentThatStopAndSearchFair,
                                          crimeTheft,crimeViolence, crimePublicDisorder, Confidence, resolutionYes, logPay, logjobDensity, Female, Other,
                                          X10.17, X18.24, X25.34, over.34, Asian, Black, Other.1, searchReasonCriminal, searchReasonDrugs, outcomeUnsuitableForSearch))
data_useful_nocovid_c <- data_nocovid %>% subset(select=c(Month, Ward.name, qLivedInAreaForYears, qWorriedAboutCrimeInArea, qConfidentThatStopAndSearchFair,
                                                          crimeTheft,crimeViolence, crimePublicDisorder, Confidence, resolutionYes, logPay, logjobDensity, Female, Other,
                                                          X10.17, X18.24, X25.34, over.34, Asian, Black, Other.1, searchReasonCriminal, searchReasonDrugs, outcomeUnsuitableForSearch))

pdata_c <- pdata.frame(data_useful_c[, c(2,1,3:ncol(data_useful_c))])
pdata_nocovid_c <- pdata.frame(data_useful_nocovid_c[, c(2,1,3:ncol(data_useful_nocovid_c))])


pdata_c <- pdata_c %>%
  group_by(Ward.name) %>%
  arrange(Ward.name, Month)


### DEFINE FORMULAS
remove_c <- c("Confidence","Month", "Ward.name")
formula_confidence <- as.formula(paste("Confidence ~", paste(setdiff(colnames(data_useful_c), remove_c), collapse= " + ")))
formula_confidence

### TEST FOR MULTICOLLINEARITY
# testmodel <- lm(Confidence ~ ., data=data_useful_c)
# ld.vars <- attributes(alias(testmodel)$Complete)$dimnames[[1]]
# ld.vars
# vif(testmodel)
## testmodel
## resolutionNo, crimeOther, Male, under.10, White. searchReasonFirearms,
## outcomeSuitableForSearch all dropped from the above df's due to
## high multicollinearity

# ### PERFORM STATISTICAL TESTS TOO CHOOSE A SUITABLE MODEL
#
# F_test_fixed <- function(data_useful){ # F-test for fixed effect
#   pooled <- lm(Confidence ~ .-Month -Ward.name, data=data_useful)
#   R2_pooled <- summary(pooled)$r.squared
#   print(R2_pooled)
#   summary(pooled)
#
#   LSDV <- lm(Confidence ~ ., data=data_useful)
#   R2_LSDC <- summary(LSDV)$r.squared
#   print(R2_LSDC)
#   summary(R2_LSDC)
#
#   nT <- nrow(data_useful)
#   n <- length(unique(data_useful$Ward.name))
#   k <- ncol(data_useful) - 1
#   print(nT)
#   print(n)
#   print(k)
#
#   F_stat <- ((R2_LSDC - R2_pooled)/(n-1))/((1 - R2_LSDC)/(nT-n-k))
#   print(F_stat)
#   return(pf(F_stat, n-1, nT-n-k) <= 0.05)
# }
# fixed_result <- F_test_fixed(data_useful_c)
# fixed_result_nocovid <- F_test_fixed(data_useful_nocovid_c)
#
# fixed_result
# fixed_result_nocovid

## Testing for presence of fixed individual (ward) and time effects

gp_c <- plm(formula_confidence, data = pdata_c, model = "pooling")
gi_c <- plm(update(formula_confidence, reformulate(c(".", "Ward.name"))), data = pdata_c, model = "pooling")
gt_c <- plm(update(formula_confidence, reformulate(c(".", "Month"))), data = pdata_c, model = "pooling")
gd_c <- plm(update(formula_confidence, reformulate(c(".", "Month + Ward.name"))), data = pdata_c, model = "pooling")


sprintf("Fixed individual effect in all data: %s", pFtest(gi_c, gp_c)$p.value <= 0.05)
sprintf("Fixed time effect in all data: %s", pFtest(gt_c, gp_c)$p.value <= 0.05)
sprintf("Fixed mixed effect in all data: %s", pFtest(gd_c, gp_c)$p.value <= 0.05)

# All data has both time and individual effects

gp_c_cov <- plm(formula_confidence, data = pdata_nocovid_c, model = "pooling")
gi_c_cov <- plm(update(formula_confidence, reformulate(c(".", "Ward.name"))), data = pdata_nocovid_c, model = "pooling")
gt_c_cov <- plm(update(formula_confidence, reformulate(c(".", "Month"))), data = pdata_nocovid_c, model = "pooling")
gd_c_cov <- plm(update(formula_confidence, reformulate(c(".", "Month + Ward.name"))), data = pdata_nocovid_c, model = "pooling")

sprintf("Fixed individual effect in non-covid data: %s", pFtest(gi_c_cov, gp_c_cov)$p.value <= 0.05)
sprintf("Fixed time effect in non-covid data: %s", pFtest(gt_c_cov, gp_c_cov)$p.value<= 0.05)
sprintf("Fixed mixed effect in non-covid data: %s", pFtest(gd_c_cov, gp_c_cov)$p.value<= 0.05)

# Non-covid data has all time, individual and mixed effects

## Testing for presence of random individual (ward) and time effects (Breush-Pagan 1980)

sprintf("Random individual effect in all data: %s", plmtest(gp_c, type="bp", effect="individual")$p.value <= 0.05)
sprintf("Random time effect in all data: %s", plmtest(gp_c, type="bp", effect="time")$p.value<= 0.05)
sprintf("Random mixed effect in all data: %s", plmtest(gp_c, type="ghm", effect="twoways")$p.value<= 0.05) # ghm is only available for twoways, but robust for unbalanced panel

sprintf("Random individual effect in non-covid data: %s", plmtest(gp_c_cov, type="bp", effect="individual")$p.value <= 0.05)
sprintf("Random time effect in non-covid data: %s", plmtest(gp_c_cov, type="bp", effect="time")$p.value<= 0.05)
sprintf("Random mixed effect in non-covid data: %s", plmtest(gp_c_cov, type="ghm", effect="twoways")$p.value<= 0.05) # ghm is only available for twoways, but robust for unbalanced panel

# In both data cases, only time  (and mixed) random effect present

## Testing which model is better (fixed effect vs random effect; mixed and time)

wi <- plm(formula_confidence, data = pdata_c, model = "within", effect='twoways')
re <- plm(formula_confidence, data = pdata_c, model = "random", effect='twoways')

wi_time <- plm(formula_confidence, data = pdata_c, model = "within", effect='time')
re_time <- plm(formula_confidence, data = pdata_c, model = "random", effect='time')

wi_cov <- plm(formula_confidence, data = pdata_nocovid_c, model = "within", effect='twoways')
re_cov <- plm(formula_confidence, data = pdata_nocovid_c, model = "random", effect='twoways')

wi_time_cov <- plm(formula_confidence, data = pdata_nocovid_c, model = "within", effect='time')
re_time_cov <- plm(formula_confidence, data = pdata_nocovid_c, model = "random", effect='time')

phtest(wi,re) # Reject alternative: random effects preferred
phtest(wi_time,re_time) # Reject null: fixed effects preferred
phtest(wi_cov, re_cov) # Reject alternative: random effects preferred
phtest(wi_time_cov, re_time_cov) # Reject null: fixed effects preferred

# Results signify that the time effects may be correlated with at least one of the regressors -> thus, we need to use the fixed-effect model
# Furthermore, we can use consider only the time effect in cases on non-covid data.


# Thus, the final best model specifications are:
# - Fixed effect model with twoways effect using all data
# - Fixed effect model with time effect using non-covid data

### ANALYSIS

final_model_all <- wi_time
final_model_nocov <- wi_time_cov

summary(final_model_all)
summary(final_model_nocov)


### FURTHER ANALYSIS -> PUTTING MORE ATTENTION TO CERTAIN CATEGORIES


nocovid_c_f <- data %>% subset(select=c(Month, Ward.name, qLivedInAreaForYears, qWorriedAboutCrimeInArea,
                                qConfidentThatStopAndSearchFair, Confidence, crimeTheft,
                                crimeViolence,Anti.social.behaviour,Criminal.damage.and.arson, resolutionYes,
                                Public.order,Possession.of.weapons, Drugs, logPay, logjobDensity, Female, Other,X10.17, X18.24,
                                X25.34, over.34, Asian, Black, Other.1, searchReasonCriminal, searchReasonDrugs, outcomeUnsuitableForSearch))

data_nocovid_c <- pdata.frame(nocovid_c_f[, c(2,1,3:ncol(nocovid_c_f))])

data_nocovid_c <- data_nocovid_c %>%
  group_by(Ward.name) %>%
  arrange(Ward.name, Month)

form_c <- as.formula(paste("Confidence ~", paste(setdiff(colnames(nocovid_c_f), remove_c), collapse= " + ")))
form_c
# model <- lm(Confidence ~ ., data=data_nocovid_c)
# vars <- attributes(alias(model)$Complete)$dimnames[[1]]
# vars
# vif(model)
# model
# resolutionYes has 10.37 :(

final_cov <-  plm(form_c, data = data_nocovid_c, model = "random", effect='time')
summary(final_cov)

##################################################### BOROUGH LEVEL ########################################################################
### LOAD LIBRARIES
library(plm)
library(dplyr)
library(lubridate)
library(foreign)
library(modelsummary)
library(car)
library(Hmisc)

rm(list=ls())
set.seed(10294)

### LOAD DATA
data = read.csv("C:/Users/hetvi/Downloads/all_joined_month_ward.csv")

data$logPay <- log(data$Pay)
data$logjobDensity<- log(data$jobDensity)
data <- data %>% subset(Month < "2020-04")
borough_list <- data %>% subset(select=c(Borough.name_x, Borough.name_y, Borough.name))

data_c <- data %>% select(-c(X,qGoodJobLocal, qGoodJobLondon, qReliedOnToBeThere, qTreatEveryoneFairly,
                          qDealWithWhatMattersToTheCommunity, qListenToConcerns, qInformedLocal, qInformedLondon,
                          Trust, qPoliceHeldAccountable,Borough.name_x, Year_x,Unnamed..0_y, crimeTheft,
                          crimeViolence, crimePublicDisorder, crimeOther, resolutionNo, resolutionYes, Pay,
                          jobDensity, Borough.name_y, Year_y, Unnamed..0.1_y, Unnamed..0, searchReasonCriminal,
                          searchReasonDrugs, searchReasonFirearms, outcomeUnsuitableForSearch, outcomeSuitableForSearch,
                          Unnamed..0.1_x, Year, White, Suspect.summonsed.to.court, Unable.to.prosecute.suspect, under.10,
                          Violent.crime, Public.disorder.and.weapons, Under.investigation, Police.and.Criminal.Evidence.Act.1984..section.1.,
                          Ward.name, Male, A.no.further.action.disposal, Community.resolution))

pdata <- pdata.frame(data_c[, c(2,1,3:ncol(data_c))])

pdata <- aggregate(. ~ Borough.name + Month, data=pdata, sum)

pdata <- pdata %>%
  group_by(Borough.name, Month) %>%
  arrange(Borough.name, Month)


### DEFINE FORMULAS
remove_c <- c("Confidence","Month", "Borough.name")
formula_confidence <- as.formula(paste("Confidence ~", paste(setdiff(colnames(pdata), remove_c), collapse= " + ")))
formula_confidence

### TEST FOR MULTICOLLINEARITY
# testmodel <- lm(Confidence ~ ., data=pdata)
# ld.vars <- attributes(alias(testmodel)$Complete)$dimnames[[1]]
# ld.vars
# vif(testmodel)
# testmodel
## resolutionNo, crimeOther, Male, under.10, White. searchReasonFirearms,
## outcomeSuitableForSearch all dropped from the above df's due to
## high multicollinearity

# ### PERFORM STATISTICAL TESTS TOO CHOOSE A SUITABLE MODEL
#
# F_test_fixed <- function(data_useful){ # F-test for fixed effect
#   pooled <- lm(Confidence ~ .-Month -Ward.name, data=data_useful)
#   R2_pooled <- summary(pooled)$r.squared
#   print(R2_pooled)
#   summary(pooled)
#
#   LSDV <- lm(Confidence ~ ., data=data_useful)
#   R2_LSDC <- summary(LSDV)$r.squared
#   print(R2_LSDC)
#   summary(R2_LSDC)
#
#   nT <- nrow(data_useful)
#   n <- length(unique(data_useful$Ward.name))
#   k <- ncol(data_useful) - 1
#   print(nT)
#   print(n)
#   print(k)
#
#   F_stat <- ((R2_LSDC - R2_pooled)/(n-1))/((1 - R2_LSDC)/(nT-n-k))
#   print(F_stat)
#   return(pf(F_stat, n-1, nT-n-k) <= 0.05)
# }
# fixed_result <- F_test_fixed(data_useful_c)
# fixed_result_nocovid <- F_test_fixed(data_useful_nocovid_c)
#
# fixed_result
# fixed_result_nocovid

## Testing for presence of fixed individual (ward) and time effects

gp_c <- plm(formula_confidence, data = pdata, model = "pooling")
gi_c <- plm(update(formula_confidence, reformulate(c(".", "Borough.name"))), data = pdata, model = "pooling")
gt_c <- plm(update(formula_confidence, reformulate(c(".", "Month"))), data = pdata, model = "pooling")
gd_c <- plm(update(formula_confidence, reformulate(c(".", "Month + Borough.name"))), data = pdata, model = "pooling")
#what am  i doing

sprintf("Fixed individual effect in no covid data: %s", pFtest(gi_c, gp_c)$p.value <= 0.05)
sprintf("Fixed time effect in no covid data: %s", pFtest(gt_c, gp_c)$p.value <= 0.05)
sprintf("Fixed mixed effect in no covid data: %s", pFtest(gd_c, gp_c)$p.value <= 0.05)

# Nocovid data has both time and individual effects

## Testing for presence of random individual (ward) and time effects (Breush-Pagan 1980)

sprintf("Random individual effect in no covid data: %s", plmtest(gp_c, type="bp", effect="individual")$p.value <= 0.05)
sprintf("Random time effect in no covid data: %s", plmtest(gp_c, type="bp", effect="time")$p.value<= 0.05)
sprintf("Random mixed effect in no covid data: %s", plmtest(gp_c, type="ghm", effect="twoways")$p.value<= 0.05) # ghm is only available for twoways, but robust for unbalanced panel

# Data has random individual and time effects

## Testing which model is better (fixed effect vs random effect; mixed and time)

wi <- plm(formula_confidence, data = pdata, model = "within", effect='twoways')
re <- plm(formula_confidence, data = pdata, model = "random", effect='twoways', random.method = "walhus")

wi_time <- plm(formula_confidence, data = pdata, model = "within", effect='time')
re_time <- plm(formula_confidence, data = pdata, model = "random", effect='time', random.method = "walhus")

phtest(wi,re) # Reject null: fixed effects preferred
phtest(wi_time,re_time) # Reject alternative: random effects preferred

# Results signify that the time effects may be correlated with at least one of the regressors -> thus, we need to use the fixed-effect model
# Furthermore, we can use consider only the time effect in cases on non-covid data.

# Thus, the final best model specifications are:
# - Fixed effect model with twoways effect using all data
# - Fixed effect model with time effect using non-covid data

### ANALYSIS

final_model <- re_time

summary(final_model)