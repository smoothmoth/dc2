library(plm)
library(dplyr)
library(lubridate)
library(foreign)

#
# data = read.csv("C:/Users/hetvi/Downloads/street_month_borough.csv")
#
# #summary(data)
#
# #Convert to dataframe and keep index the unit of analysis and date
# pdata <- data.frame(data, index = c("Month", "Borough.name"))
# pdata$Month <- parse_date_time(pdata$Month, orders = "ym") #makes sure column is date time
#
# #Organises data so that the data for each borough is consecutive and in date order
# organized_data <- pdata %>%
#   group_by(Borough.name) %>%
#   arrange(Borough.name, Month)
#
# f_data <- as.data.frame(organized_data)
#
# # # To check if the data organisation worked
# # filtered_data <- f_data %>%
# #   filter(Borough.name== "Westminster") %>%
# #   select(Borough.name,Month)
# # filtered_data
#
# # #To check if the panel data is balanced
# # borough_counts <- count(f_data, Borough.name)
# # print(borough_counts)
# # # All counts are 158 so we have balanced data and dont have to worry about bias in that term
#
# # Make fake Y value column for now
# set.seed(123)  # For reproducibility
# f_data$trust <- runif(nrow(organized_data))
# f_data$trust <- round(f_data$trust, digits = 3)
#
# ## MODELLING
#
# # Pooled OLS model
# f_data <- f_data[, -which(names(f_data) %in% c("X", "Unnamed..0", "Year"))]
#
# # pooling_model <- plm(trust ~ Pay + resolutionYes + Bicycle.theft, data = f_data,index= c("Borough.name","Month"),model = "pooling")
# # summary(pooling_model)
#
# remove <- f_data[, -which(names(f_data) %in% c("index", "trust"))]
#
# factors <- c(colnames(remove))
#
# form <- as.formula(paste("trust ~ ", paste(factors, collapse="+")))
#
# pooling_model <- plm(form, data = f_data,index= c("Borough.name","Month"),model = "pooling")
# summary(pooling_model)
#
# # Fixed effects model
# fe_model <- plm(form,index= c("Borough.name","Month"), data = f_data, model = "within")
# summary(fe_model)
#
# # Random effects model - SOMETHING IS WRONGGGG
# re_model <- plm(form,index= c("Borough.name","Month"), data = f_data, model = "random")
# summary(re_model)
#
# # Hausman test
# phtest(fe_model, re_model)
#
# # LSDV
# lsdv <-lm(form, data=f_data)
# summary(lsdv)
#
# new <- read.csv("C:/Users/hetvi/Downloads/search_month_borough.csv")
# newdata <- data.frame(new, index = c("Month", "Borough.name"))
# newdata$Month <- parse_date_time(newdata$Month, orders = "ym")
#
# all = left_join(f_data, newdata, by=c("Month"="Month", "Borough.name"="Borough.name"))
#


# Load the dataset

data <- read.csv("C:/Users/hetvi/Downloads/street_year_borough.csv")
new <- read.csv("C:/Users/hetvi/Downloads/search_year_borough.csv")


#Convert to dataframe and keep index the unit of analysis and date

pdata <- data.frame(data, index = c("Year", "Borough.name"))
# pdata$Month <- parse_date_time(pdata$Month, orders = "ym")
newdata <- data.frame(new, index = c("Year", "Borough.name"))
# newdata$Month <- parse_date_time(newdata$Month, orders = "ym")


# Join data

all = left_join(pdata, newdata, by=c("Year"="Year", "Borough.name"="Borough.name"))


#Organises data so that the data for each borough is consecutive and in date order

organized_data <- all %>%
  group_by(Borough.name) %>%
  arrange(Borough.name, Year)

f_data <- as.data.frame(organized_data)

# # To check if the data organisation worked
# filtered_data <- f_data %>%
#   filter(Borough.name== "Westminster") %>%
#   select(Borough.name,Month)
# filtered_data

# #To check if the panel data is balanced
# borough_counts <- count(f_data, Borough.name)
# print(borough_counts)
# # All counts are 158 so we have balanced data and dont have to worry about bias in that term

f_data <- subset(f_data, Year > 2015)

f_data <- subset(f_data, Year < 2022)

# Filter the Columns to keep

columns_to_keep <- c(
  "searchReasonCriminal", "searchReasonDrugs", "searchReasonFirearms",
  "outcomeUnsuitableForSearch", "outcomeSuitableForSearch",
  "crimeTheft", "crimeViolence", "crimePublicDisorder", "crimeOther",
  "resolutionNo", "resolutionYes", "Female", "Pay", "jobDensity",
  "Male", "Other", "X10.17", "X18.24", "X25.34", "over.34", "under.10",
  "Asian", "Black", "Other.1", "White", "Year", "Borough.name"
)


f_data <- f_data %>%
  select(all_of(columns_to_keep))

# Error of singularity

# Min-max scaling function
min_max_scale <- function(x) {
  scaled <- (x - min(x)) / (max(x) - min(x))
  return(round(scaled, 3))
}

# Apply min-max scaling to all columns except 'trust'
f_data <- f_data %>%
  mutate(across(-c(Borough.name,Year), min_max_scale))

# PAS data
pas = read.csv("C:/Users/hetvi/Downloads/clean_PAS.csv")
pas_clean <- pas[, -which(names(pas) %in% c("X", "Month", "Ward.code", "Ward.name", "Q60", "Q61", "Q62C", "NQ135BH","Confidence"))]

join <- left_join(f_data, pas_clean, by=c("Year"="Year", "Borough.name"="Borough.name"))

agg <- join %>%
  group_by(Borough.name, Year) %>%
  summarise(across(everything(), ~ mean(.x, na.rm = TRUE)), .groups = 'drop')


re_org <- agg %>%
  group_by(Borough.name) %>%
  arrange(Borough.name, Year)

df_f <- as.data.frame(re_org)

df_f <- subset(df_f, Year <2021)

df_f <- df_f %>%
  rename(trust = NQ135BD)

# To make the formula for the model
remove <- df_f[, -which(names(df_f) %in% c("trust"))]


factors <- c(colnames(remove))

form <- as.formula(paste("trust ~ ", paste(factors, collapse="+")))



## MODELS

# Pooled OLS model

pooling_model <- plm(form, data = df_f,index= c("Borough.name","Year"),model = "pooling")
summary(pooling_model)

# Fixed effects model

fe_model <- plm(form,index= c("Borough.name","Year"), data = df_f, model = "within")
summary(fe_model)

# Random effects model - SOMETHING IS WRONGGGG - more columns than entities

re_model <- plm(form,index= c("Borough.name","Year"), data = df_f, model = "random")
summary(re_model)

# Hausman test

phtest(fe_model, re_model)

# LSDV
lsdv <-lm(form, data=f_data)
summary(lsdv)

