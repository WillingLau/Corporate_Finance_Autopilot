import logging
from app.models.finance import CompanyProfile, YearlyFinancials
from app.models.forecast import ScenarioAssumptions, ScenarioResult, FinancialModelOutput

logger = logging.getLogger(__name__)

class FinancialEngine:
    @staticmethod
    def calculate_cagr(beginning_value: float, ending_value: float, years: int) -> float:
        if beginning_value <= 0 or years <= 0:
            return 0.0
        return (ending_value / beginning_value) ** (1 / years) - 1

    @staticmethod
    def _project_scenario(
        scenario_name: str, 
        last_actual: YearlyFinancials, 
        growth_rate: float, 
        assumptions: ScenarioAssumptions
    ) -> ScenarioResult:
        forecasts = []
        current_revenue = last_actual.total_revenue
        last_year_int = int(last_actual.year)

        for i in range(1, assumptions.forecast_years + 1):
            next_year_str = str(last_year_int + i)
            projected_revenue = current_revenue * (1 + growth_rate)
            projected_net_income = projected_revenue * assumptions.target_net_margin
            
            forecast = YearlyFinancials(
                year=next_year_str,
                total_revenue=projected_revenue,
                net_income=projected_net_income,
                operating_income=0.0
            )
            forecasts.append(forecast)
            current_revenue = projected_revenue

        return ScenarioResult(
            scenario_name=scenario_name,
            assumed_growth_rate=growth_rate,
            forecast_data=forecasts
        )

    def run_forecast(self, company_data: CompanyProfile, assumptions: ScenarioAssumptions) -> FinancialModelOutput:
        logger.info(f"Running forecast for {company_data.ticker}...")
        
        historical = company_data.historical_financials
        if len(historical) < 2:
            raise ValueError("Insufficient historical data to compute CAGR.")

        first_year_data = historical[0]
        last_year_data = historical[-1]
        years_diff = int(last_year_data.year) - int(first_year_data.year)
        
        historical_cagr = self.calculate_cagr(
            beginning_value=first_year_data.total_revenue,
            ending_value=last_year_data.total_revenue,
            years=years_diff
        )
        logger.info(f"Historical CAGR: {historical_cagr:.2%}")

        base_rate = historical_cagr + assumptions.base_revenue_cagr_modifier
        upside_rate = base_rate + assumptions.upside_modifier
        downside_rate = base_rate + assumptions.downside_modifier

        base_case = self._project_scenario("Base Case", last_year_data, base_rate, assumptions)
        upside_case = self._project_scenario("Upside Case", last_year_data, upside_rate, assumptions)
        downside_case = self._project_scenario("Downside Case", last_year_data, downside_rate, assumptions)

        logger.info("Forecast calculations complete.")

        return FinancialModelOutput(
            historical_cagr=historical_cagr,
            base_case=base_case,
            upside_case=upside_case,
            downside_case=downside_case
        )