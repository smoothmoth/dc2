### LOAD LIBRARIES
library(plm)
library(dplyr)
library(lubridate)
library(foreign)
library(modelsummary)
library(Hmisc)
library(car)

rm(list=ls())
set.seed(10294)

### LOAD DATA
data = read.csv("C:/Users/hetvi/Downloads/all_joined.csv")

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
                                                      Offender.given.drugs.possession.warning, Penalty.Notice.for.Disorder, Summons...charged.by.post, Suspect.arrested))

pdata <- pdata.frame(data_c[, c(2,1,3:ncol(data_c))])

pdata <- aggregate(. ~ Ward.name + Month, data=pdata, sum)

### DEFINE FORMULAS
remove_c <- c("Confidence","Month", "Ward.name")
formula_confidence <- as.formula(paste("Confidence ~", paste(setdiff(colnames(pdata), remove_c), collapse= " + ")))
formula_confidence

### TEST FOR MULTICOLLINEARITY
testmodel <- lm(Confidence ~ ., data=pdata)
ld.vars <- attributes(alias(testmodel)$Complete)$dimnames[[1]]
ld.vars
vif(testmodel)
testmodel
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
gi_c <- plm(update(formula_confidence, reformulate(c(".", "Ward.name"))), data = pdata, model = "pooling")
gt_c <- plm(update(formula_confidence, reformulate(c(".", "Month"))), data = pdata, model = "pooling")
gd_c <- plm(update(formula_confidence, reformulate(c(".", "Month + Ward.name"))), data = pdata, model = "pooling")


sprintf("Fixed individual effect in no covid data: %s", pFtest(gi_c, gp_c)$p.value <= 0.05)
sprintf("Fixed time effect in no covid data: %s", pFtest(gt_c, gp_c)$p.value <= 0.05)
sprintf("Fixed mixed effect in no covid data: %s", pFtest(gd_c, gp_c)$p.value <= 0.05)

# Nocovid data has all effects

## Testing for presence of random individual (ward) and time effects (Breush-Pagan 1980)

sprintf("Random individual effect in no covid data: %s", plmtest(gp_c, type="bp", effect="individual")$p.value <= 0.05)
sprintf("Random time effect in no covid data: %s", plmtest(gp_c, type="bp", effect="time")$p.value<= 0.05)
sprintf("Random mixed effect in no covid data: %s", plmtest(gp_c, type="ghm", effect="twoways")$p.value<= 0.05) # ghm is only available for twoways, but robust for unbalanced panel

# Data has all random effects

## Testing which model is better (fixed effect vs random effect; mixed and time)

wi <- plm(formula_confidence, data = pdata, model = "within", effect='twoways')
re <- plm(formula_confidence, data = pdata, model = "random", effect='twoways', random.method = "amemiya")

wi_time <- plm(formula_confidence, data = pdata, model = "within", effect='time')
re_time <- plm(formula_confidence, data = pdata, model = "random", effect='time',  random.method = "amemiya")

phtest(wi,re) # Reject null: fixed effects preferred
phtest(wi_time,re_time) # Reject alternative: random effects preferred

# Results signify that the time effects may be correlated with at least one of the regressors -> thus, we need to use the fixed-effect model
# Furthermore, we can use consider only the time effect in cases on non-covid data.

# Thus, the final best model specifications are:
# - Fixed effect model with twoways effect using all data
# - Fixed effect model with time effect using non-covid data

### ANALYSIS

final_model <- wi_time

summary(final_model)
