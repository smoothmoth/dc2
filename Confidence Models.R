### LOAD LIBRARIES
library(plm)
library(dplyr)
library(lubridate)
library(foreign)
library(modelsummary)
library(car)

rm(list=ls())

### LOAD DATA
data = read.csv("C:/Users/hetvi/Downloads/all_joined_month_ward.csv")

data$logPay <- log(data$Pay)
data$logjobDensity<- log(data$jobDensity)
data_nocovid <- data %>% subset(Month < "2020-04")

borough_list <- data %>% subset(select=c(Borough.name_x, Borough.name_y, Borough.name))

data_useful_c <- data %>% subset(select=c(Month, Ward.name, qLivedInAreaForYears, qWorriedAboutCrimeInArea,logjobDensity, Female, Other,X10.17, X18.24,
                                          qConfidentThatStopAndSearchFair, Confidence, crimeTheft,resolutionNo, crimeOther, under.10, White,
                                          outcomeSuitableForSearch,crimeViolence, crimePublicDisorder, resolutionYes, logPay,  
                                          X25.34, Asian, Black, searchReasonCriminal))
data_useful_nocovid_c <- data_nocovid %>% subset(select=c(Month, Ward.name, qLivedInAreaForYears, qWorriedAboutCrimeInArea,logjobDensity, Female, Other,X10.17, X18.24,
                                                          qConfidentThatStopAndSearchFair, Confidence, crimeTheft,resolutionNo, crimeOther, Male, under.10, White,
                                                          searchReasonFirearms, outcomeSuitableForSearch,crimeViolence, crimePublicDisorder, resolutionYes, logPay,  
                                                          X25.34, Asian, Black, searchReasonCriminal))

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
testmodel <- lm(Confidence ~ ., data=data_useful_c)
ld.vars <- attributes(alias(testmodel)$Complete)$dimnames[[1]]
ld.vars
vif(testmodel)
testmodel
# outcomeUnsuitableForSearch, Asian, crimeViolence are 8-9 
# other variables have moderate collinearity

### PERFORM STATISTICAL TESTS TOO CHOOSE A SUITABLE MODEL

F_test_fixed <- function(data_useful){ # F-test for fixed effect
  pooled <- lm(Trust ~ .-Month -Ward.name, data=data_useful)
  R2_pooled <- summary(pooled)$r.squared

  LSDV <- lm(Trust ~ ., data=data_useful)
  R2_LSDC <- summary(LSDV)$r.squared

  nT <- nrow(data_useful)
  n <- length(unique(data_useful$Ward.name))
  k <- ncol(data_useful) - 1
  # print(nT)
  # print(n)  
  # print(k)

  F_stat <- ((R2_LSDC - R2_pooled)/(n-1))/((1 - R2_LSDC)/(nT-n-k))
  print(F_stat)
  return(pf(F_stat, n-1, nT-n-k) <= 0.05)
}
fixed_result <- F_test_fixed(data_useful_c)
fixed_result_nocovid <- F_test_fixed(data_useful_nocovid_c)

fixed_result
fixed_result_nocovid

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


c_f <- data %>% subset(select=c(Month, Ward.name, qLivedInAreaForYears, qWorriedAboutCrimeInArea, 
                                qConfidentThatStopAndSearchFair, Confidence, crimeTheft, 
                                crimeViolence,Anti.social.behaviour,Criminal.damage.and.arson, 
                                Public.order,Possession.of.weapons, Drugs, logPay, logjobDensity, Female, Other,X10.17, X18.24,
                                Offender.sent.to.prison, Offender.given.community.sentence, Local.resolution_x,
                                Offender.given.penalty.notice_x, Offender.given.drugs.possession.warning,
                                Offender.given.conditional.discharge,Defendant.found.not.guilty,
                                Offender.given.a.caution, Offender.fined, Offender.given.suspended.prison.sentence,
                                Offender.deprived.of.property,Offender.otherwise.dealt.with, Offender.ordered.to.pay.compensation,
                                Suspect.charged.as.part.of.another.case,Offender.given.absolute.discharge,
                                X25.34, over.34, Asian, Black, Other.1, searchReasonCriminal, searchReasonDrugs, outcomeUnsuitableForSearch))

nocovid_c_f <- data_nocovid %>% subset(select=c(Month, Ward.name, qLivedInAreaForYears, qWorriedAboutCrimeInArea, 
                                                qConfidentThatStopAndSearchFair, Confidence, crimeTheft, 
                                                crimeViolence,Anti.social.behaviour,Criminal.damage.and.arson,
                                                Public.order,Possession.of.weapons, Drugs, logPay, logjobDensity, Female, Other,X10.17, X18.24,
                                                Offender.sent.to.prison, Offender.given.community.sentence, Local.resolution_x,
                                                Offender.given.penalty.notice_x, Offender.given.drugs.possession.warning,
                                                Offender.given.conditional.discharge,Defendant.found.not.guilty,
                                                Offender.given.a.caution, Offender.fined, Offender.given.suspended.prison.sentence,
                                                Offender.deprived.of.property,Offender.otherwise.dealt.with, Offender.ordered.to.pay.compensation,
                                                Suspect.charged.as.part.of.another.case,Offender.given.absolute.discharge,
                                                X25.34, over.34, Asian, Black, Other.1, searchReasonCriminal, searchReasonDrugs, outcomeUnsuitableForSearch))

data_c <- pdata.frame(c_f[, c(2,1,3:ncol(c_f))])
data_nocovid_c <- pdata.frame(nocovid_c_f[, c(2,1,3:ncol(nocovid_c_f))])

data_c <- data_c %>%
  group_by(Ward.name) %>%
  arrange(Ward.name, Month)

data_nocovid_c <- data_nocovid_c %>%
  group_by(Ward.name) %>%
  arrange(Ward.name, Month)

form_c <- as.formula(paste("Confidence ~", paste(setdiff(colnames(c_f), remove_c), collapse= " + ")))
model <- lm(Confidence ~ ., data=data_c)
vars <- attributes(alias(model)$Complete)$dimnames[[1]] 
vars
vif(model)
model
# resolutionYes has 10.37 :(

final_all <- plm(form_c, data = data_c, model = "random", effect='time')
final_cov <-  plm(form_c, data = data_nocovid_c, model = "random", effect='time')
summary(final_all)
summary(final_cov)