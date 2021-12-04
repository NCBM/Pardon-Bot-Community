#include <libqalculate/Calculator.h>

bool update_exchange_rate()
{
    auto calc = Calculator();
    return (int)(!calc.fetchExchangeRates());
}
