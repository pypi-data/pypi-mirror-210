from sharetop.core.capital_flow.capital_flow_monitor import get_real_time_capital_flow, get_history_bill, get_sector_real_time_capital_flow
from enum import Enum
# d = {"a": 1, "b":2}
# d = get_real_time_capital_flow(["002714", "300033"])
# d = get_real_time_capital_flow(['002714', '300033'])
# d = get_sector_real_time_capital_flow('area', '10')

d = get_real_time_capital_flow("000001")

print(d)
print(d.to_dict("records"))


