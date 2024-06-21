### LOAD LIBRARIES
library(plm)
library(dplyr)
library(lubridate)
library(foreign)
library(modelsummary)
library(car)
library(Hmisc)
library(lmtest)

rm(list=ls())
set.seed(10294)

############################ TRUST MODEL ###############################################

### LOAD DATA
data = read.csv("all_joined.csv")

data$logPay <- log(data$Pay)
data$logjobDensity<- log(data$jobDensity)
data <- data %>% subset(Month < "2020-04")
borough_list <- data %>% subset(select=c(Borough.name_x, Borough.name_y, Borough.name))

data_useful <- data %>% select(-c(X,Borough.name_x, Year_x,Unnamed..0_y, crimeTheft, Confidence,
                                  crimeViolence, crimePublicDisorder, crimeOther, Pay, jobDensity, Borough.name_y, Year_y,
                                  Unnamed..0.1_y, Unnamed..0, resolutionNo, outcomeSuitableForSearch,
                                  Unnamed..0.1_x, Year, White, Suspect.summonsed.to.court, Unable.to.prosecute.suspect, under.10,
                                  Violent.crime, Public.disorder.and.weapons, Under.investigation, Police.and.Criminal.Evidence.Act.1984..section.1.,
                                  Borough.name, Male, A.no.further.action.disposal, Community.resolution, respondentGender_Other,
                                  respondentEthnicity_Others, respondentAge_65.or.over, Unnamed..0_x, Court.result.unavailable,
                                  Court.case.unable.to.proceed,Awaiting.court.outcome,Formal.action.is.not.in.the.public.interest,
                                  Unable.to.prosecute.suspect,Defendant.sent.to.Crown.Court, Offender.sent.to.prison, Offender.given.community.sentence,
                                  Local.resolution_y,Offender.given.penalty.notice_y, Offender.given.a.drugs.possession.warning,Offender.given.conditional.discharge,
                                  Defendant.found.not.guilty, Offender.given.a.caution,Offender.fined,Offender.given.suspended.prison.sentence,
                                  Offender.deprived.of.property,Offender.otherwise.dealt.with, Offender.ordered.to.pay.compensation,
                                  Suspect.charged.as.part.of.another.case,Offender.given.absolute.discharge,
                                  Investigation.complete..no.suspect.identified,Local.resolution_x, Offender.given.penalty.notice_x,
                                  Status.update.unavailable, Criminal.Justice.Act.1988..section.139B. , Criminal.Justice.and.Public.Order.Act.1994..section.60. ,
                                  Firearms.Act.1968..section.47.,Misuse.of.Drugs.Act.1971..section.23.,Arrest,Article.found...Detailed.outcome.unavailable,
                                  Caution..simple.or.conditional.,Khat.or.Cannabis.warning, Nothing.found...no.further.action, Offender.cautioned,
                                  Offender.given.drugs.possession.warning, Penalty.Notice.for.Disorder, Summons...charged.by.post, Suspect.arrested,
                                  X10.17, searchReasonFirearms))

pdata_nocovid_t <- pdata.frame(data_useful[, c(2,1,3:ncol(data_useful))])

### DEFINE FORMULAS 
remove_t <- c("Trust", "Month", "Ward.name")
formula_trust <- as.formula(paste("Trust ~", paste(setdiff(colnames(data_useful), remove_t), collapse= " + ")))

### TEST FOR MULTICOLLINEARITY
testmodel <- lm(Trust ~ . - Month - Ward.name, data=data_useful)
ld.vars <- attributes(alias(testmodel)$Complete)$dimnames[[1]]
ld.vars
vif(testmodel)


# resolutionNo, Male, under.10, White, searchReasonFirearms, X10.17,
# outcomeSuitableForSearch,  all dropped from the above df's due to 
# high multicollinearity

### PERFORM STATISTICAL TESTS TO CHOOSE A SUITABLE MODEL

## Testing for presence of fixed individual (ward) and time effects

gp_t_cov <- plm(formula_trust, data = pdata_nocovid_t, model = "pooling")
gi_t_cov <- plm(update(formula_trust, reformulate(c(".", "Ward.name"))), data = pdata_nocovid_t, model = "pooling")
gt_t_cov <- plm(update(formula_trust, reformulate(c(".", "Month"))), data = pdata_nocovid_t, model = "pooling")

sprintf("Fixed individual effect in non-covid data: %s", pFtest(gi_t_cov, gp_t_cov)$p.value <= 0.05)
sprintf("Fixed time effect in non-covid data: %s", pFtest(gt_t_cov, gp_t_cov)$p.value<= 0.05)


# Data has only the time effect (and mixed effect too)

## Testing for presence of random individual (ward) and time effects (Breush-Pagan 1980)

sprintf("Random individual effect in non-covid data: %s", plmtest(gp_t_cov, type="bp", effect="individual")$p.value <= 0.05)
sprintf("Random time effect in non-covid data: %s", plmtest(gp_t_cov, type="bp", effect="time")$p.value<= 0.05)


fix <- plm(formula_trust, data = pdata_nocovid_t, model="within",effect='time')
rand <-  plm(formula_trust, data = pdata_nocovid_t, model="random",effect='time')
## Because of a huge number of regressors, we think that it is really probable that the error term could be correlated with at least one of the
## regressors. Thus, we will use a fixed effect model.


# Thus, the final best model specifications are: 
# - Fixed effect model with time effect using non-covid data

### ANALYSIS

## Initial analysis
final_model_trust <- plm(formula_trust, data = pdata_nocovid_t, model = "within", effect='time')

## CHECK AUTOCORRELATION
# H0: no autocorrelation -> p < 0.05, reject H0, we have serial correlation
pbgtest(final_model_trust)
# autocorrelation present

## CHECK HOMOSKEDASTICITY
# H0: there is homoscedasticity -> p < 0.05, reject H0, we have heteroskedasticity
bptest(formula_trust, data=pdata_nocovid_t, studentize=F)

# homoskedasticity present


# ==> to mitigate both of these problems, we can use robust standard errors to
# - ensure a correct output despite heteroskedasticity and autocorrelation.
# This bypasses these problems but makes your results robust and reliable.

coeftest(final_model_trust, vcovHC(final_model_trust, method="arellano"))



## In depth analysis of most significant questions

### Load data
in_depth_data <- read.csv('PAS_in_depth.csv')
in_depth_data$logPay <- log(in_depth_data$Pay)
in_depth_data$logjobDensity<- log(in_depth_data$jobDensity)
in_depth_data <- in_depth_data %>% subset(Month < "2020-04")
data_in_depth <- in_depth_data %>% select(-c(X,Borough.name_x, Year_x,Unnamed..0_y, crimeTheft, Confidence,
                                             crimeViolence, crimePublicDisorder, crimeOther, Pay, jobDensity, Borough.name_y, Year_y,
                                             Unnamed..0.1_y, resolutionNo, outcomeSuitableForSearch,
                                             Unnamed..0.1_x, Year, White, Suspect.summonsed.to.court, Unable.to.prosecute.suspect, under.10,
                                             Violent.crime, Public.disorder.and.weapons, Under.investigation, Police.and.Criminal.Evidence.Act.1984..section.1.,
                                             Borough.name, Male, A.no.further.action.disposal, Community.resolution, respondentGender_Other,
                                             respondentEthnicity_Others, respondentAge_65.or.over, Unnamed..0_x, Court.result.unavailable,
                                             Court.case.unable.to.proceed,Awaiting.court.outcome,Formal.action.is.not.in.the.public.interest,
                                             Unable.to.prosecute.suspect,Defendant.sent.to.Crown.Court, Offender.sent.to.prison, Offender.given.community.sentence,
                                             Local.resolution_y,Offender.given.penalty.notice_y, Offender.given.a.drugs.possession.warning,Offender.given.conditional.discharge,
                                             Defendant.found.not.guilty, Offender.given.a.caution,Offender.fined,Offender.given.suspended.prison.sentence,
                                             Offender.deprived.of.property,Offender.otherwise.dealt.with, Offender.ordered.to.pay.compensation,
                                             Suspect.charged.as.part.of.another.case,Offender.given.absolute.discharge,
                                             Investigation.complete..no.suspect.identified,Local.resolution_x, Offender.given.penalty.notice_x,
                                             Status.update.unavailable, Criminal.Justice.Act.1988..section.139B. , Criminal.Justice.and.Public.Order.Act.1994..section.60. ,
                                             Firearms.Act.1968..section.47.,Misuse.of.Drugs.Act.1971..section.23.,Arrest,Article.found...Detailed.outcome.unavailable,
                                             Caution..simple.or.conditional.,Khat.or.Cannabis.warning, Nothing.found...no.further.action, Offender.cautioned,
                                             Offender.given.drugs.possession.warning, Penalty.Notice.for.Disorder, Summons...charged.by.post, Suspect.arrested,
                                             X10.17, searchReasonFirearms, qTreatEveryoneFairly_Neither.agree.nor.disagree,
                                             qReliedOnToBeThere_Neither.agree.nor.disagree, qPoliceHeldAccountable_Neither.agree.nor.disagree, 
                                             qPoliceHeldAccountable_Not.Asked, qPoliceHeldAccountable_Refused, qPoliceHeldAccountable_Don.t.know,
                                             qReliedOnToBeThere, qGoodJobLondon, qPoliceHeldAccountable, qTreatEveryoneFairly, qConfidentThatStopAndSearchFair))

pdata_in_depth <- pdata.frame(data_in_depth[, c(2,1,3:ncol(data_in_depth))])

### Define formulas
remove_t <- c("Trust", "Month", "Ward.name")
formula_trust_d <- as.formula(paste("Trust ~", paste(setdiff(colnames(data_in_depth), remove_t), collapse= " + ")))

wi_in_depth_t <- plm(formula_trust_d, data=pdata_in_depth, model='within', effect='time')
print(coeftest(wi_in_depth_t, vcovHC(wi_in_depth_t, method="arellano")))

### Different models for R^2

pooled <- plm(formula_trust, data = pdata_nocovid_t, model = "pooling", effect='time')
fem <- plm(formula_trust, data = pdata_nocovid_t, model = "within", effect='time')
rem <- plm(formula_trust, data = pdata_nocovid_t, model = "random", effect='time', random.method = "amemiya")
fem_depth <- plm(formula_trust_d, data = pdata_in_depth, model = "within", effect='time')

sprintf("Pooled R^2: %s", summary(pooled)$r.squared)
sprintf("FEM R^2:%s", summary(fem)$r.squared)
sprintf("REM R^2:%s", summary(rem)$r.squared)
sprintf("FEM in-depth R^2:%s", summary(fem_depth)$r.squared)
############################ CONFIDENCE MODEL ###############################################

### LOAD LIBRARIES
library(plm)
library(dplyr)
library(lubridate)
library(foreign)
library(modelsummary)
library(Hmisc)
library(car)
library(lmtest)

rm(list=ls())
set.seed(10294)

### LOAD DATA
data = read.csv("all_joined.csv")

data$logPay <- log(data$Pay)
data$logjobDensity<- log(data$jobDensity)
data <- data %>% subset(Month < "2020-04")
borough_list <- data %>% subset(select=c(Borough.name_x, Borough.name_y, Borough.name))

data_c <- data %>% select(-c(X,qGoodJobLocal, qGoodJobLondon, qReliedOnToBeThere, qTreatEveryoneFairly,
                             qDealWithWhatMattersToTheCommunity, qListenToConcerns, qInformedLocal, qInformedLondon,
                             Trust, qPoliceHeldAccountable,Borough.name_x, Year_x,Unnamed..0_y, crimeTheft,
                             crimeViolence, crimePublicDisorder, crimeOther, Pay, jobDensity, Borough.name_y, Year_y,
                             Unnamed..0.1_y, Unnamed..0, resolutionNo, outcomeSuitableForSearch,
                             Unnamed..0.1_x, Year, White, Suspect.summonsed.to.court, Unable.to.prosecute.suspect, under.10,
                             Violent.crime, Public.disorder.and.weapons, Under.investigation, Police.and.Criminal.Evidence.Act.1984..section.1.,
                             Borough.name, Male, A.no.further.action.disposal, Community.resolution, respondentGender_Other,
                             respondentEthnicity_Others, respondentAge_65.or.over, Unnamed..0_x, Court.result.unavailable,
                             Court.case.unable.to.proceed,Awaiting.court.outcome,Formal.action.is.not.in.the.public.interest,
                             Unable.to.prosecute.suspect,Defendant.sent.to.Crown.Court, Offender.sent.to.prison, Offender.given.community.sentence,
                             Local.resolution_y,Offender.given.penalty.notice_y, Offender.given.a.drugs.possession.warning,Offender.given.conditional.discharge,
                             Defendant.found.not.guilty, Offender.given.a.caution,Offender.fined,Offender.given.suspended.prison.sentence,
                             Offender.deprived.of.property,Offender.otherwise.dealt.with, Offender.ordered.to.pay.compensation,
                             Suspect.charged.as.part.of.another.case,Offender.given.absolute.discharge,
                             Investigation.complete..no.suspect.identified,Local.resolution_x, Offender.given.penalty.notice_x,
                             Status.update.unavailable, Criminal.Justice.Act.1988..section.139B. , Criminal.Justice.and.Public.Order.Act.1994..section.60. ,
                             Firearms.Act.1968..section.47.,Misuse.of.Drugs.Act.1971..section.23.,Arrest,Article.found...Detailed.outcome.unavailable,
                             Caution..simple.or.conditional.,Khat.or.Cannabis.warning, Nothing.found...no.further.action, Offender.cautioned,
                             Offender.given.drugs.possession.warning, Penalty.Notice.for.Disorder, Summons...charged.by.post, Suspect.arrested,
                             X10.17, searchReasonFirearms))

pdata <- pdata.frame(data_c[, c(2,1,3:ncol(data_c))])

pdata <- aggregate(. ~ Ward.name + Month, data=pdata, sum)

### DEFINE FORMULAS
remove_c <- c("Confidence","Month", "Ward.name")
formula_confidence <- as.formula(paste("Confidence ~", paste(setdiff(colnames(pdata), remove_c), collapse= " + ")))
formula_confidence

### TEST FOR MULTICOLLINEARITY
testmodel <- lm(Confidence ~ .-Month -Ward.name, data=pdata)
ld.vars <- attributes(alias(testmodel)$Complete)$dimnames[[1]]
ld.vars
vif(testmodel)
testmodel
## resolutionNo, crimeOther, Male, under.10, White. searchReasonFirearms,
## outcomeSuitableForSearch all dropped from the above df's due to
## high multicollinearity



# Because the data is largely the same, we use the same model specification as for trust modelling:
# - Fixed effect model with mixed effect using non-covid data

### ANALYSIS

final_model_conf <-  plm(formula_confidence, data = pdata, model = "within", effect='time')


## CHECK AUTOCORRELATION
# H0: no autocorrelation -> p < 0.05, reject H0, we have serial correlation
pbgtest(final_model_conf)
# autocorrelation present

## CHECK HOMOSKEDASTICITY
# H0: there is homoscedasticity -> p < 0.05, reject H0, we have heteroskedasticity
bptest(formula_confidence, data=pdata, studentize=F)

# homoskedasticity present


# ==> to mitigate both of these problems, we can use robust standard errors to
# - ensure a correct output despite heteroskedasticity and autocorrelation.
# This bypasses these problems but makes your results robust and reliable.

coeftest(final_model_conf, vcovHC(final_model_conf, method="arellano"))
#summary(final_model_conf)

## In depth analysis of most significant questions

### Load data
in_depth_data <- read.csv('PAS_in_depth.csv')
in_depth_data$logPay <- log(in_depth_data$Pay)
in_depth_data$logjobDensity<- log(in_depth_data$jobDensity)
in_depth_data <- in_depth_data %>% subset(Month < "2020-04")
data_in_depth <- in_depth_data %>% select(-c(X,qGoodJobLocal, qGoodJobLondon, qReliedOnToBeThere, qTreatEveryoneFairly,
                                             qDealWithWhatMattersToTheCommunity, qListenToConcerns, qInformedLocal, qInformedLondon,
                                             qPoliceHeldAccountable,Borough.name_x, Year_x,Unnamed..0_y, crimeTheft, Trust,
                                             crimeViolence, crimePublicDisorder, crimeOther, Pay, jobDensity, Borough.name_y, Year_y,
                                             Unnamed..0.1_y, resolutionNo, outcomeSuitableForSearch,
                                             Unnamed..0.1_x, Year, White, Suspect.summonsed.to.court, Unable.to.prosecute.suspect, under.10,
                                             Violent.crime, Public.disorder.and.weapons, Under.investigation, Police.and.Criminal.Evidence.Act.1984..section.1.,
                                             Borough.name, Male, A.no.further.action.disposal, Community.resolution, respondentGender_Other,
                                             respondentEthnicity_Others, respondentAge_65.or.over, Unnamed..0_x, Court.result.unavailable,
                                             Court.case.unable.to.proceed,Awaiting.court.outcome,Formal.action.is.not.in.the.public.interest,
                                             Unable.to.prosecute.suspect,Defendant.sent.to.Crown.Court, Offender.sent.to.prison, Offender.given.community.sentence,
                                             Local.resolution_y,Offender.given.penalty.notice_y, Offender.given.a.drugs.possession.warning,Offender.given.conditional.discharge,
                                             Defendant.found.not.guilty, Offender.given.a.caution,Offender.fined,Offender.given.suspended.prison.sentence,
                                             Offender.deprived.of.property,Offender.otherwise.dealt.with, Offender.ordered.to.pay.compensation,
                                             Suspect.charged.as.part.of.another.case,Offender.given.absolute.discharge,
                                             Investigation.complete..no.suspect.identified,Local.resolution_x, Offender.given.penalty.notice_x,
                                             Status.update.unavailable, Criminal.Justice.Act.1988..section.139B. , Criminal.Justice.and.Public.Order.Act.1994..section.60. ,
                                             Firearms.Act.1968..section.47.,Misuse.of.Drugs.Act.1971..section.23.,Arrest,Article.found...Detailed.outcome.unavailable,
                                             Caution..simple.or.conditional.,Khat.or.Cannabis.warning, Nothing.found...no.further.action, Offender.cautioned,
                                             Offender.given.drugs.possession.warning, Penalty.Notice.for.Disorder, Summons...charged.by.post, Suspect.arrested,
                                             X10.17, searchReasonFirearms, qTreatEveryoneFairly_Neither.agree.nor.disagree,
                                             qReliedOnToBeThere_Neither.agree.nor.disagree, qPoliceHeldAccountable_Neither.agree.nor.disagree, 
                                             qPoliceHeldAccountable_Not.Asked, qPoliceHeldAccountable_Refused, qPoliceHeldAccountable_Don.t.know,
                                             qReliedOnToBeThere, qGoodJobLondon, qPoliceHeldAccountable, qTreatEveryoneFairly, qConfidentThatStopAndSearchFair))

pdata_in_depth <- pdata.frame(data_in_depth[, c(2,1,3:ncol(data_in_depth))])

### Define formulas
remove_c <- c("Confidence", "Month", "Ward.name")
formula_confidence_d <- as.formula(paste("Confidence ~", paste(setdiff(colnames(data_in_depth), remove_c), collapse= " + ")))

wi_in_depth_c <- plm(formula_confidence_d, data=pdata_in_depth, model='within', effect='time')

coeftest(wi_in_depth_c, vcovHC(wi_in_depth_c, method="arellano"))

### Different models for R^2

pooled <- plm(formula_confidence, data = pdata, model = "pooling", effect='time')
fem <- plm(formula_confidence, data = pdata, model = "within", effect='time')
rem <- plm(formula_confidence, data = pdata, model = "random", effect='time', random.method = "amemiya")
fem_depth <- plm(formula_confidence_d, data = pdata_in_depth, model = "within", effect='time')

sprintf("Pooled R^2: %s", summary(pooled)$r.squared)
sprintf("FEM R^2:%s", summary(fem)$r.squared)
sprintf("REM R^2:%s", summary(rem)$r.squared)
sprintf("FEM in depthR^2:%s", summary(fem_depth)$r.squared)

############################ STOP AND SEARCH MODEL ###############################################
rm(list=ls())
library(tidyverse)
library(caTools)
library(dplyr)
library(lubridate)
library(foreign)
library(modelsummary)
library(car)
library(Hmisc)
library(plm)
library(lmtest)

data = read.csv('Final.csv')

data <- data %>% subset(select=-c(Male, White))
set.seed(123) # for reproducibility
split <- sample.split(data$outcomeUnsuitableForSearch, SplitRatio = 0.7)
training_set <- subset(data, split == TRUE)
testing_set <- subset(data, split == FALSE)

model <- glm(outcomeUnsuitableForSearch ~ ., data = training_set, family = binomial)
summary(model)

testmodel <- lm(outcomeUnsuitableForSearch ~ ., data=data)
ld.vars <- attributes(alias(testmodel)$Complete)$dimnames[[1]]
ld.vars
vif(testmodel)
testmodel

## CHECK AUTOCORRELATION
# H0: no autocorrelation -> p < 0.05, reject H0, we have serial correlation
pbgtest(model)

## CHECK HOMOSCEDASTICITY
# H0: there is homoscedasticity -> p < 0.05, reject H0, we have heteroskedasticity
bptest(outcomeUnsuitableForSearch ~., data=data, studentize=F)


# ==> to mitigate both of these problems, we can use robust standard errors to
# - ensure a correct output despite heteroskedasticity and autocorrelation.
# This bypasses these problems but makes your results robust and reliable.
coeftest(model, vcovHC(model, method="arellano"))

### Test accuracy

testing_set$prob <- predict(model, testing_set, type='response')
testing_set$pred <- ifelse(testing_set$prob > 0.5, yes=1, no=0)
testing_set$accurate <- ifelse(testing_set$pred == testing_set$outcomeUnsuitableForSearch, yes=0, no=1)
print(sum(testing_set$accurate)/nrow(testing_set))

