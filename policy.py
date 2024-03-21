import numpy as np
import datetime as dt
import pandas as pd

class Policy:
    # class attributes
    
    product = "ING LifePay Plus Base"
    step_up = 0.06
    step_up_period = 10
    rider_charge_rate = 0.0085

    initial_premium = 100000.0
    first_wd_age = 70
    annuity_start_age = 80
    last_death_age = 100
    mortality = 0.005
    wd_rate = 0.03
    rb_target = 0.2

    m_and_e = 0.014
    fund_fees = 0.0015
    risk_free_rate = 0.03
    volatility = 0.16

    maw_age1 = 59.5
    maw_rate1 = 0.04

    maw_age2 = 65
    maw_rate2 = 0.05

    maw_age3 = 76
    maw_rate3 = 0.06

    maw_age4 = 80
    maw_rate4 = 0.07

    start_age = 60
    yrs = 41

    fund1_pre_fee_initial = 0.16
    fund2_pre_fee_initial = 0.64

    def __init__(self):
        self.year = np.arange(self.yrs)
        self.age = np.arange(self.start_age, self.start_age + self.yrs)

        self.anniversary = []
        for i in range(self.yrs):
            d = dt.date(2016+i, 8, 1)
            self.anniversary.append(d.isoformat())

        self.contribution = np.zeros(self.yrs)
        self.av_pre_fee = np.zeros(self.yrs)
        self.fund1_pre_fee = np.zeros(self.yrs)
        self.fund2_pre_fee = np.zeros(self.yrs)

        self.m_and_e_fund_fees = np.zeros(self.yrs)

        self.av_pre_wd = np.zeros(self.yrs)
        self.fund1_pre_wd = np.zeros(self.yrs)
        self.fund2_pre_wd = np.zeros(self.yrs)

        self.av_post_wd = np.zeros(self.yrs)
        self.fund1_post_wd = np.zeros(self.yrs)
        self.fund2_post_wd = np.zeros(self.yrs)

        self.rider_charge = np.zeros(self.yrs)

        self.av_post_charge = np.zeros(self.yrs)
        self.fund1_post_charge = np.zeros(self.yrs)
        self.fund2_post_charge = np.zeros(self.yrs)

        self.death_payment = np.zeros(self.yrs)

        self.av_post_death_claim = np.zeros(self.yrs)

        self.fund1_post_death_claim = np.zeros(self.yrs)
        self.fund2_post_death_claim = np.zeros(self.yrs)
        self.fund1_post_rb = np.zeros(self.yrs)
        self.fund2_post_rb = np.zeros(self.yrs)

        self.rop_death_base = np.zeros(self.yrs)
        self.nar_death_claim = np.zeros(self.yrs)

        self.death_benefit_base = np.zeros(self.yrs)
        self.wd_base = np.zeros(self.yrs)
        self.wd_amount = np.zeros(self.yrs)
        self.cumulative_wd = np.zeros(self.yrs)
        self.max_annual_wd = np.zeros(self.yrs)
        self.max_annual_wd_rate = np.zeros(self.yrs)

        self.eligible_step_up = np.zeros((self.yrs,), dtype=int) # index 0 not relevant
        self.growth_phase = np.zeros((self.yrs,), dtype=int) # index 0 not relevant
        self.wd_phase = np.zeros((self.yrs,), dtype=int) # index 0 not relevant
        self.auto_periodic_benefit_status = np.zeros((self.yrs,), dtype=int) # index 0 not relevant
        self.last_death = np.zeros((self.yrs,), dtype=int) # index 0 not relevant

        self.fund1_return = np.zeros(self.yrs) # index 0 not relevant
        self.fund2_return = np.zeros(self.yrs) # index 0 not relevant

        self.rebalance_indicator = np.zeros((self.yrs,), dtype=int)
        self.df = np.zeros(self.yrs)

        self.qx = self.mortality * np.ones(self.yrs)

        self.death_claim = np.zeros(self.yrs) # same as nar_death_claim
        self.wd_claim = np.zeros(self.yrs)

        self.pv_db_claim = 0.0
        self.pv_wb_claim = 0.0
        self.pv_rc = 0.0

    def generate_fund2_return(self):
        for i in range(self.yrs):
            if (i > 0):
                self.fund2_return[i] = np.exp(np.log(1+self.risk_free_rate)-0.5*(self.volatility**2)+self.volatility*np.random.standard_normal()) - 1

    def manually_input_fund2_return(self, fund2_return):
        self.fund2_return = fund2_return

    def calculate(self):
        for i in range(self.yrs):
            if (i > 0):
                self.fund1_return[i] = self.risk_free_rate

        for i in range(self.yrs):
            self.df[i] = (1 + self.risk_free_rate) ** (-self.year[i])

        for i in range(self.yrs):
            if (i > 0):
                if ((self.age[i] <= self.first_wd_age) and (self.age[i] <= self.annuity_start_age) and (self.age[i] < self.last_death_age)):
                    self.growth_phase[i] = 1
                else:
                    self.growth_phase[i] = 0

        for i in range(self.yrs):
            if (i > 0):
                if ((self.year[i] <= self.step_up_period) and (self.growth_phase[i] == 1)):
                    self.eligible_step_up[i] = 1
                else:
                    self.eligible_step_up[i] = 0

        for i in range(self.yrs):
            if (i > 0):
                if (self.age[i] == self.last_death_age):
                    self.last_death[i] = 1
                else:
                    self.last_death[i] = 0

        self.max_annual_wd_rate[0] = 0.0
        for i in range(self.yrs):
            if (i > 0):
                if (self.growth_phase[i] == 1):
                    self.max_annual_wd_rate[i] = 0.0
                else:
                    if (self.age[i] > self.maw_age4):
                        self.max_annual_wd_rate[i] = self.maw_rate4
                    else:
                        if (self.age[i] > self.maw_age3):
                            self.max_annual_wd_rate[i] = self.maw_rate3
                        else:
                            if (self.age[i] > self.maw_age2):
                                self.max_annual_wd_rate[i] = self.maw_rate2
                            else:
                                if (self.age[i] > self.maw_age1):
                                    self.max_annual_wd_rate[i] = self.maw_rate1
                                else:
                                    self.max_annual_wd_rate[i] = 0.0

        self.fund1_pre_fee[0] = self.initial_premium * self.fund1_pre_fee_initial
        self.fund2_pre_fee[0] = self.initial_premium * self.fund2_pre_fee_initial
        self.av_pre_fee[0] = self.fund1_pre_fee[0] + self.fund2_pre_fee[0]

        self.m_and_e_fund_fees[0] = 0.0
        self.av_pre_wd[0] = self.av_pre_fee[0] + self.contribution[0] - self.m_and_e_fund_fees[0]

        if (self.av_pre_wd[0] == 0.0):
            self.fund1_pre_wd[0] = 0.0
        else:
            self.fund1_pre_wd[0] = self.fund1_pre_fee[0] * (self.av_pre_wd[0] / self.av_pre_fee[0])

        if (self.av_pre_wd[0] == 0.0):
            self.fund2_pre_wd[0] = 0.0
        else:
            self.fund2_pre_wd[0] = self.fund2_pre_fee[0] * (self.av_pre_wd[0] / self.av_pre_fee[0])

        self.av_post_wd[0] = self.av_pre_wd[0]

        if (self.av_post_wd[0] == 0.0):
            self.fund1_post_wd[0] = 0.0
        else:
            self.fund1_post_wd[0] = self.fund1_pre_wd[0] * (self.av_post_wd[0] / self.av_pre_wd[0])

        if (self.av_post_wd[0] == 0.0):
            self.fund2_post_wd[0] = 0.0
        else:
            self.fund2_post_wd[0] = self.fund2_pre_wd[0] * (self.av_post_wd[0] / self.av_pre_wd[0])

        self.rider_charge[0] = 0.0

        self.av_post_charge[0] = self.av_post_wd[0] - self.rider_charge[0]

        if (self.av_post_charge[0] == 0.0):
            self.fund1_post_charge[0] = 0.0
        else:
            self.fund1_post_charge[0] = self.fund1_post_wd[0] * (self.av_post_charge[0] / self.av_post_wd[0])

        if (self.av_post_charge[0] == 0.0):
            self.fund2_post_charge[0] = 0.0
        else:
            self.fund2_post_charge[0] = self.fund2_post_wd[0] * (self.av_post_charge[0] / self.av_post_wd[0])

        self.death_payment[0] = 0.0

        self.av_post_death_claim[0] = np.max([self.av_post_charge[0]-self.death_payment[0],0.0])

        if (self.av_post_death_claim[0] == 0.0):
            self.fund1_post_death_claim[0] = 0.0
        else:
            self.fund1_post_death_claim[0] = self.fund1_post_charge[0] * (self.av_post_death_claim[0] / self.av_post_charge[0])

        if (self.av_post_death_claim[0] == 0.0):
            self.fund2_post_death_claim[0] = 0.0
        else:
            self.fund2_post_death_claim[0] = self.fund2_post_charge[0] * (self.av_post_death_claim[0] / self.av_post_charge[0])

        self.rebalance_indicator[0] = 0

        if (self.rebalance_indicator[0] == 1):
            self.fund1_post_rb[0] = self.av_post_death_claim[0] * self.rb_target
        else:
            self.fund1_post_rb[0] = self.fund1_post_death_claim[0]

        self.fund2_post_rb[0] = self.av_post_charge[0] - self.fund1_post_rb[0]

        self.rop_death_base[0] = self.initial_premium

        self.nar_death_claim[0] = np.max([0.0,self.death_payment[0]-self.av_post_charge[0]])

        self.death_benefit_base[0] = self.initial_premium

        self.wd_base[0] = self.initial_premium

        self.wd_amount[0] = 0.0

        self.max_annual_wd[0] = 0.0

        self.wd_claim[0] = 0.0

        self.auto_periodic_benefit_status[1] = 0

        for i in range(self.yrs):
            if ((i > 0) and (i <= 10)):
                self.fund1_pre_fee[i] = self.fund1_post_rb[i-1] * (1 + self.fund1_return[i])
                self.fund2_pre_fee[i] = self.fund2_post_rb[i-1] * (1 + self.fund2_return[i])
                self.av_pre_fee[i] = self.fund1_pre_fee[i] + self.fund2_pre_fee[i]

                self.m_and_e_fund_fees[i] = self.av_post_death_claim[i-1] * (self.m_and_e + self.fund_fees)

                self.av_pre_wd[i] = np.max([0.0, self.av_pre_fee[i]+self.contribution[i]-self.m_and_e_fund_fees[i]])

                if (self.av_pre_wd[i] == 0.0):
                    self.fund1_pre_wd[i] = 0.0
                else:
                    self.fund1_pre_wd[i] = self.fund1_pre_fee[i] * (self.av_pre_wd[i] / self.av_pre_fee[i])
                
                if (self.av_pre_wd[i] == 0.0):
                    self.fund2_pre_wd[i] = 0.0
                else:
                    self.fund2_pre_wd[i] = self.fund2_pre_fee[i] * (self.av_pre_wd[i] / self.av_pre_fee[i])
                
                if (((self.age[i] > self.first_wd_age) or (self.age[i] > self.annuity_start_age)) and (self.av_post_death_claim[i-1] > 0.0)
                    and (self.age[i] < self.last_death_age)): # for i == 1, 2, ..., 10, wd_phase[i] == 0
                    self.wd_phase[i] = 1
                else: # wd_phase[40] == 0
                    self.wd_phase[i] = 0
                
                if (i > 1):
                    if (self.age[i] >= self.last_death_age): # auto_periodic_benefit_status[40] == 0
                        self.auto_periodic_benefit_status[i] = 0
                    else:
                        if ((self.wd_phase[i-1] == 1) and (self.av_post_death_claim[i-1] == 0.0)):
                            self.auto_periodic_benefit_status[i] = 1
                        else: # for i == 1, 2, ..., 11, auto_periodic_benefit_status[i] == 0
                            self.auto_periodic_benefit_status[i] = self.auto_periodic_benefit_status[i-1]
                
                if (self.wd_phase[i] == 1):
                    self.wd_amount[i] = self.wd_rate * self.wd_base[i]
                else:
                    if (self.auto_periodic_benefit_status[i] == 1):
                        self.wd_amount[i] = self.max_annual_wd[i]
                    else: # for i == 0, 1, ..., 10, wd_amount[i] == 0.0
                        self.wd_amount[i] = 0.0
                
                self.av_post_wd[i] = np.max([0.0, self.av_pre_wd[i]-self.wd_amount[i]])

                if (self.av_post_wd[i] == 0.0):
                    self.fund1_post_wd[i] = 0.0
                else:
                    self.fund1_post_wd[i] = self.fund1_pre_wd[i] * (self.av_post_wd[i] / self.av_pre_wd[i])
                
                if (self.av_post_wd[i] == 0.0):
                    self.fund2_post_wd[i] = 0.0
                else:
                    self.fund2_post_wd[i] = self.fund2_pre_wd[i] * (self.av_post_wd[i] / self.av_pre_wd[i])
                
                self.rider_charge[i] = self.rider_charge_rate * self.av_post_wd[i]

                self.av_post_charge[i] = self.av_post_wd[i] - self.rider_charge[i]

                if (self.av_post_charge[i] == 0.0):
                    self.fund1_post_charge[i] = 0.0
                else:
                    self.fund1_post_charge[i] = self.fund1_post_wd[i] * (self.av_post_charge[i] / self.av_post_wd[i])
                
                if (self.av_post_charge[i] == 0.0):
                    self.fund2_post_charge[i] = 0.0
                else:
                    self.fund2_post_charge[i] = self.fund2_post_wd[i] * (self.av_post_charge[i] / self.av_post_wd[i])

                if (self.growth_phase[i] + self.wd_phase[i] + self.auto_periodic_benefit_status[i] + self.last_death[i] == 0):
                    self.death_payment[i] = 0.0
                else:
                    self.death_payment[i] = np.max([self.death_benefit_base[i-1], self.rop_death_base[i-1]]) * self.qx[i]
                
                self.av_post_death_claim[i] = np.max([self.av_post_charge[i] - self.death_payment[i], 0.0])

                if (self.av_post_death_claim[i] == 0.0):
                    self.fund1_post_death_claim[i] = 0.0
                else:
                    self.fund1_post_death_claim[i] = self.fund1_post_charge[i] * (self.av_post_death_claim[i] / self.av_post_charge[i])
                
                if (self.av_post_death_claim[i] == 0.0):
                    self.fund2_post_death_claim[i] = 0.0
                else:
                    self.fund2_post_death_claim[i] = self.fund2_post_charge[i] * (self.av_post_death_claim[i] / self.av_post_charge[i])
                
                self.rebalance_indicator[i] = self.wd_phase[i] + self.auto_periodic_benefit_status[i]

                if (self.rebalance_indicator[i] == 1):
                    self.fund1_post_rb[i] = self.av_post_death_claim[i] * self.rb_target
                else:
                    self.fund1_post_rb[i] = self.fund1_post_death_claim[i]
                
                self.fund2_post_rb[i] = self.av_post_charge[i] - self.fund1_post_rb[i]

                self.rop_death_base[i] = self.rop_death_base[i-1] * (1 - self.qx[i])

                self.nar_death_claim[i] = np.max([0.0, self.death_payment[i] - self.av_post_charge[i]])

                self.death_benefit_base[i] = np.max([0.0,
                                                self.death_benefit_base[i-1] * (1 - self.qx[i]) + self.contribution[i] - self.m_and_e_fund_fees[i] - self.wd_amount[i-1] - self.rider_charge[i]])

                temp1 = 0.0
                if (self.growth_phase[i] == 1):
                    temp1 = self.av_post_death_claim[i]
                else:
                    temp1 = 0.0
                temp2 = 0.0
                if (self.eligible_step_up[i] == 1):
                    temp2 = self.wd_base[i-1] * (1 - self.qx[i]) * (1 + self.step_up) + self.contribution[i] - self.m_and_e_fund_fees[i] - self.rider_charge[i]
                else:
                    temp2 = 0.0
                self.wd_base[i] = np.max([temp1,
                                    self.wd_base[i-1] * (1 - self.qx[i]) + self.contribution[i],
                                    temp2])
                
                self.max_annual_wd[i] = self.max_annual_wd_rate[i] * self.wd_base[i]

                self.wd_claim[i] = np.max([self.wd_amount[i] - self.av_post_death_claim[i-1], 0.0])
            
            if (i > 10):
                self.fund1_pre_fee[i] = self.fund1_post_rb[i-1] * (1 + self.fund1_return[i])
                self.fund2_pre_fee[i] = self.fund2_post_rb[i-1] * (1 + self.fund2_return[i])
                self.av_pre_fee[i] = self.fund1_pre_fee[i] + self.fund2_pre_fee[i]

                self.m_and_e_fund_fees[i] = self.av_post_death_claim[i-1] * (self.m_and_e + self.fund_fees)

                self.av_pre_wd[i] = np.max([0.0, self.av_pre_fee[i]+self.contribution[i]-self.m_and_e_fund_fees[i]])

                if (self.av_pre_wd[i] == 0.0):
                    self.fund1_pre_wd[i] = 0.0
                else:
                    self.fund1_pre_wd[i] = self.fund1_pre_fee[i] * (self.av_pre_wd[i] / self.av_pre_fee[i])
                
                if (self.av_pre_wd[i] == 0.0):
                    self.fund2_pre_wd[i] = 0.0
                else:
                    self.fund2_pre_wd[i] = self.fund2_pre_fee[i] * (self.av_pre_wd[i] / self.av_pre_fee[i])
                
                if (((self.age[i] > self.first_wd_age) or (self.age[i] > self.annuity_start_age)) and (self.av_post_death_claim[i-1] > 0.0)
                    and (self.age[i] < self.last_death_age)): # for i == 1, 2, ..., 10, wd_phase[i] == 0
                    self.wd_phase[i] = 1
                else: # wd_phase[40] == 0
                    self.wd_phase[i] = 0
                
                if (i > 1):
                    if (self.age[i] >= self.last_death_age): # auto_periodic_benefit_status[40] == 0
                        self.auto_periodic_benefit_status[i] = 0
                    else:
                        if ((self.wd_phase[i-1] == 1) and (self.av_post_death_claim[i-1] == 0.0)):
                            self.auto_periodic_benefit_status[i] = 1
                        else: # for i == 1, 2, ..., 11, auto_periodic_benefit_status[i] == 0
                            self.auto_periodic_benefit_status[i] = self.auto_periodic_benefit_status[i-1]
                
                temp1 = 0.0
                if (self.growth_phase[i] == 1):
                    temp1 = self.av_post_death_claim[i]
                else:
                    temp1 = 0.0
                temp2 = 0.0
                if (self.eligible_step_up[i] == 1):
                    temp2 = self.wd_base[i-1] * (1 - self.qx[i]) * (1 + self.step_up) + self.contribution[i] - self.m_and_e_fund_fees[i] - self.rider_charge[i]
                else:
                    temp2 = 0.0
                self.wd_base[i] = np.max([temp1,
                                    self.wd_base[i-1] * (1 - self.qx[i]) + self.contribution[i],
                                    temp2])
                
                self.max_annual_wd[i] = self.max_annual_wd_rate[i] * self.wd_base[i]

                if (self.wd_phase[i] == 1):
                    self.wd_amount[i] = self.wd_rate * self.wd_base[i]
                else:
                    if (self.auto_periodic_benefit_status[i] == 1):
                        self.wd_amount[i] = self.max_annual_wd[i]
                    else: # for i == 0, 1, ..., 10, wd_amount[i] == 0.0
                        self.wd_amount[i] = 0.0
                
                self.av_post_wd[i] = np.max([0.0, self.av_pre_wd[i]-self.wd_amount[i]])

                if (self.av_post_wd[i] == 0.0):
                    self.fund1_post_wd[i] = 0.0
                else:
                    self.fund1_post_wd[i] = self.fund1_pre_wd[i] * (self.av_post_wd[i] / self.av_pre_wd[i])
                
                if (self.av_post_wd[i] == 0.0):
                    self.fund2_post_wd[i] = 0.0
                else:
                    self.fund2_post_wd[i] = self.fund2_pre_wd[i] * (self.av_post_wd[i] / self.av_pre_wd[i])
                
                self.rider_charge[i] = self.rider_charge_rate * self.av_post_wd[i]

                self.av_post_charge[i] = self.av_post_wd[i] - self.rider_charge[i]

                if (self.av_post_charge[i] == 0.0):
                    self.fund1_post_charge[i] = 0.0
                else:
                    self.fund1_post_charge[i] = self.fund1_post_wd[i] * (self.av_post_charge[i] / self.av_post_wd[i])
                
                if (self.av_post_charge[i] == 0.0):
                    self.fund2_post_charge[i] = 0.0
                else:
                    self.fund2_post_charge[i] = self.fund2_post_wd[i] * (self.av_post_charge[i] / self.av_post_wd[i])
                
                if (self.growth_phase[i] + self.wd_phase[i] + self.auto_periodic_benefit_status[i] + self.last_death[i] == 0):
                    self.death_payment[i] = 0.0
                else:
                    self.death_payment[i] = np.max([self.death_benefit_base[i-1], self.rop_death_base[i-1]]) * self.qx[i]
                
                self.av_post_death_claim[i] = np.max([self.av_post_charge[i] - self.death_payment[i], 0.0])

                if (self.av_post_death_claim[i] == 0.0):
                    self.fund1_post_death_claim[i] = 0.0
                else:
                    self.fund1_post_death_claim[i] = self.fund1_post_charge[i] * (self.av_post_death_claim[i] / self.av_post_charge[i])
                
                if (self.av_post_death_claim[i] == 0.0):
                    self.fund2_post_death_claim[i] = 0.0
                else:
                    self.fund2_post_death_claim[i] = self.fund2_post_charge[i] * (self.av_post_death_claim[i] / self.av_post_charge[i])
                
                self.rebalance_indicator[i] = self.wd_phase[i] + self.auto_periodic_benefit_status[i]

                if (self.rebalance_indicator[i] == 1):
                    self.fund1_post_rb[i] = self.av_post_death_claim[i] * self.rb_target
                else:
                    self.fund1_post_rb[i] = self.fund1_post_death_claim[i]
                
                self.fund2_post_rb[i] = self.av_post_charge[i] - self.fund1_post_rb[i]

                self.rop_death_base[i] = self.rop_death_base[i-1] * (1 - self.qx[i])

                self.nar_death_claim[i] = np.max([0.0, self.death_payment[i] - self.av_post_charge[i]])

                self.death_benefit_base[i] = np.max([0.0,
                                                self.death_benefit_base[i-1] * (1 - self.qx[i]) + self.contribution[i] - self.m_and_e_fund_fees[i] - self.wd_amount[i-1] - self.rider_charge[i]])
                
                self.wd_claim[i] = np.max([self.wd_amount[i] - self.av_post_death_claim[i-1], 0.0])

        self.death_claim = self.nar_death_claim

        self.cumulative_wd[0] = self.wd_amount[0]

        for i in range(self.yrs):
            if (i > 0):
                self.cumulative_wd[i] = self.cumulative_wd[i-1] + self.wd_amount[i]

        for i in range(self.yrs):
            self.pv_db_claim = self.pv_db_claim + self.nar_death_claim[i] * self.df[i]

        for i in range(self.yrs):
            self.pv_wb_claim = self.pv_wb_claim + self.wd_claim[i] * self.df[i]

        for i in range(self.yrs):
            self.pv_rc = self.pv_rc + self.rider_charge[i] * self.df[i]

    def output_to_excel(self):
        data_cashflow = pd.DataFrame({'Year': self.year,
                                'Anniversary': self.anniversary,
                                'Age': self.age,
                                'Contribution': self.contribution,
                                'AV_Pre_Fee': self.av_pre_fee,
                                'Fund1_Pre_Fee': self.fund1_pre_fee,
                                'Fund2_Pre_Fee': self.fund2_pre_fee,
                                'M_and_E_Fund_Fees': self.m_and_e_fund_fees,
                                'AV_Pre_Withdrawal': self.av_pre_wd,
                                'Fund1_Pre_Withdrawal': self.fund1_pre_wd,
                                'Fund2_Pre_Withdrawal': self.fund2_pre_wd,
                                'AV_Post_Withdrawal': self.av_post_wd,
                                'Fund1_Post_Withdrawal': self.fund1_post_wd,
                                'Fund2_Post_Withdrawal': self.fund2_post_wd,
                                'Rider_Charge': self.rider_charge,
                                'AV_Post_Charge': self.av_post_charge,
                                'Fund1_Post_Charge': self.fund1_post_charge,
                                'Fund2_Post_Charge': self.fund2_post_charge,
                                'Death_Payment': self.death_payment,
                                'AV_Post_Death_Claim': self.av_post_death_claim,
                                'Fund1_Post_Death_Claim': self.fund1_post_death_claim,
                                'Fund2_Post_Death_Claim': self.fund2_post_death_claim,
                                'Fund1_Post_Rebalance': self.fund1_post_rb,
                                'Fund2_Post_Rebalance': self.fund2_post_rb,
                                'ROP_Death_Base': self.rop_death_base,
                                'NAR_Death_Claim': self.nar_death_claim,
                                'Death_Benefit_Base': self.death_benefit_base,
                                'Withdrawal_Base': self.wd_base,
                                'Withdrawal_Amount': self.wd_amount,
                                'Cumulative_Withdrawal': self.cumulative_wd,
                                'Maximum_Annual_Withdrawal': self.max_annual_wd,
                                'Maximum_Annual_Withdrawal_Rate': self.max_annual_wd_rate,
                                'Eligible_Step_Up': self.eligible_step_up,
                                'Growth_Phase': self.growth_phase,
                                'Withdrawal_Phase': self.wd_phase,
                                'Automatic_Periodic_Benefit_Status': self.auto_periodic_benefit_status,
                                'Last_Death': self.last_death,
                                'Fund1_Return': self.fund1_return,
                                'Fund2_Return': self.fund2_return,
                                'Rebalance_Indicator': self.rebalance_indicator,
                                'DF': self.df,
                                'qx': self.qx,
                                'Death_Claim': self.death_claim,
                                'Withdrawal_Claim': self.wd_claim},
                                columns=['Year',
                                         'Anniversary',
                                         'Age',
                                         'Contribution',
                                         'AV_Pre_Fee',
                                         'Fund1_Pre_Fee',
                                         'Fund2_Pre_Fee',
                                         'M_and_E_Fund_Fees',
                                         'AV_Pre_Withdrawal',
                                         'Fund1_Pre_Withdrawal',
                                         'Fund2_Pre_Withdrawal',
                                         'AV_Post_Withdrawal',
                                         'Fund1_Post_Withdrawal',
                                         'Fund2_Post_Withdrawal',
                                         'Rider_Charge',
                                         'AV_Post_Charge',
                                         'Fund1_Post_Charge',
                                         'Fund2_Post_Charge',
                                         'Death_Payment',
                                         'AV_Post_Death_Claim',
                                         'Fund1_Post_Death_Claim',
                                         'Fund2_Post_Death_Claim',
                                         'Fund1_Post_Rebalance',
                                         'Fund2_Post_Rebalance',
                                         'ROP_Death_Base',
                                         'NAR_Death_Claim',
                                         'Death_Benefit_Base',
                                         'Withdrawal_Base',
                                         'Withdrawal_Amount',
                                         'Cumulative_Withdrawal',
                                         'Maximum_Annual_Withdrawal',
                                         'Maximum_Annual_Withdrawal_Rate',
                                         'Eligible_Step_Up',
                                         'Growth_Phase',
                                         'Withdrawal_Phase',
                                         'Automatic_Periodic_Benefit_Status',
                                         'Last_Death',
                                         'Fund1_Return',
                                         'Fund2_Return',
                                         'Rebalance_Indicator',
                                         'DF',
                                         'qx',
                                         'Death_Claim',
                                         'Withdrawal_Claim'])
        data_pv = pd.DataFrame({'PV_DB_Claim': [self.pv_db_claim],
                                'PV_WB_Claim': [self.pv_wb_claim],
                                'PV_RC': [self.pv_rc]},
                                columns=['PV_DB_Claim',
                                         'PV_WB_Claim',
                                         'PV_RC'])

        with pd.ExcelWriter('output.xlsx') as writer:
            data_cashflow.to_excel(writer, sheet_name='Cashflow')
            data_pv.to_excel(writer, sheet_name='PV')

if (__name__ == "__main__"):
    policy_1 = Policy() # instantiation
    policy_1.generate_fund2_return() # generate fund2_return
    # if you want to use a predefined fund2_return,
    # you can use the manually_input_fund2_return method.
    policy_1.calculate() # calculate cashflow and pv
    policy_1.output_to_excel() # output to excel, one sheet for cashflow, one sheet for pv