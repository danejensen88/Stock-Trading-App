document.addEventListener('DOMContentLoaded', function () {
    const stockDetailsSection = document.querySelector('.stock-details');
    const stockSymbol = stockDetailsSection.getAttribute('data-symbol');
    const isMarketOpen = JSON.parse(stockDetailsSection.getAttribute('data-market-open'));
    const currentPriceElement = stockDetailsSection.querySelector('.current-price');
    const dayHighElement = stockDetailsSection.querySelector('.day-high');
    const dayLowElement = stockDetailsSection.querySelector('.day-low');
    const transactionSection = document.getElementById('transaction-section');
    const marketClosedMessage = document.getElementById('market-closed-message');
    const chartElement = document.getElementById(`${stockSymbol}-chart`);
    const sharesInput = document.getElementById('shares');
    const totalCostDisplay = document.getElementById('total-cost');
    const dynamicPriceInput = document.getElementById('dynamic-price');

    // Check market status
    if (!isMarketOpen) {
        transactionSection.style.display = 'none'; // Hide buy/sell options
        marketClosedMessage.style.display = 'block'; // Show market closed message
        return; // Stop further updates if the market is closed
    }

    class Stock {
        constructor(symbol, initialPrice, dayHigh, dayLow) {
            this.symbol = symbol;
            this.currentPrice = parseFloat(initialPrice);
            this.dayHigh = parseFloat(dayHigh);
            this.dayLow = parseFloat(dayLow);
            this.seconds = 0;
            this.chart = null;
            this.initChart();
            this.startUpdating();
        }

        static generateRandomPriceChange(currentPrice) {
            const randomPercent = (Math.random() * 4 - 2) * 0.01; // Fluctuate by -2% to +2%
            return currentPrice * (1 + randomPercent);
        }

        initChart() {
            const ctx = chartElement.getContext('2d');
            this.chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: `${this.symbol} Stock Price`,
                        data: [],
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 2,
                        fill: false,
                    }]
                },
                options: {
                    scales: {
                        x: {
                            title: { display: true, text: 'Time (seconds)' }
                        },
                        y: {
                            title: { display: true, text: 'Price ($)' },
                            beginAtZero: false
                        }
                    }
                }
            });
        }

        updatePrice() {
            this.currentPrice = Stock.generateRandomPriceChange(this.currentPrice);
            this.seconds += 5;

            if (this.currentPrice > this.dayHigh) this.dayHigh = this.currentPrice;
            if (this.currentPrice < this.dayLow) this.dayLow = this.currentPrice;

            this.updateUI();
            this.updateBackend();

            this.chart.data.labels.push(this.seconds);
            this.chart.data.datasets[0].data.push(this.currentPrice);
            this.chart.update();

            if (this.chart.data.labels.length > 30) {
                this.chart.data.labels.shift();
                this.chart.data.datasets[0].data.shift();
            }
        }

        updateUI() {
            currentPriceElement.textContent = `$${this.currentPrice.toFixed(2)}`;
            dayHighElement.textContent = `$${this.dayHigh.toFixed(2)}`;
            dayLowElement.textContent = `$${this.dayLow.toFixed(2)}`;
            dynamicPriceInput.value = this.currentPrice.toFixed(2);

            const numberOfShares = parseFloat(sharesInput.value);
            if (numberOfShares) {
                const totalCost = numberOfShares * this.currentPrice;
                totalCostDisplay.textContent = totalCost.toLocaleString('en-US', {
                    style: 'currency',
                    currency: 'USD'
                });
            }
        }

        updateBackend() {
            fetch('/update_stock_price', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    symbol: this.symbol,
                    currentPrice: this.currentPrice,
                    dayHigh: this.dayHigh,
                    dayLow: this.dayLow,
                }),
            }).then(response => {
                if (!response.ok) {
                    console.error(`Failed to update stock price: ${response.statusText}`);
                }
            }).catch(error => {
                console.error(`Error updating stock price: ${error}`);
            });
        }

        startUpdating() {
            setInterval(() => this.updatePrice(), 5000);
        }
    }

    // Initialize the stock chart and updates
    const initialPrice = stockDetailsSection.getAttribute('data-current-price');
    const dayHigh = stockDetailsSection.getAttribute('data-day-high');
    const dayLow = stockDetailsSection.getAttribute('data-day-low');
    new Stock(stockSymbol, initialPrice, dayHigh, dayLow);
});




