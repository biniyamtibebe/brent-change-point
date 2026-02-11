# fix_setup.ps1
Write-Host "🔧 Fixing Brent Oil Price Analysis Setup" -ForegroundColor Cyan
Write-Host "=" * 60

# 1. Create necessary directories
New-Item -ItemType Directory -Force -Path r"C:\Users\hp\Pictures\brent-change-point\brent-change-point\data" | Out-Null
New-Item -ItemType Directory -Force -Path r"C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\raw" | Out-Null
Write-Host "✓ Created data directories" -ForegroundColor Green

# 2. Check if events file exists and has correct columns
$eventsPath = r"C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\raw\events.csv"
if (Test-Path $eventsPath) {
    Write-Host "✓ Found events file: $eventsPath" -ForegroundColor Green
    
    # Check column names
    $df = Import-Csv $eventsPath -Delimiter ','
    $cols = $df | Get-Member -MemberType NoteProperty | Select-Object -ExpandProperty Name
    
    Write-Host "  Columns in file: $cols" -ForegroundColor Yellow
    
    if ($cols -notcontains 'Event_Description') {
        Write-Host "  ⚠ Column 'Event_Description' not found. Renaming columns..." -ForegroundColor Yellow
        
        # Try to detect actual column names
        if ($cols -contains 'Event Description') {
            Rename-Item $eventsPath "oil_events_backup.csv" -ErrorAction SilentlyContinue
            Get-Content "oil_events_backup.csv" | ForEach-Object {
                $_ -replace 'Event Description', 'Event_Description' `
                   -replace 'Date', 'Date' `
                   -replace 'Category', 'Category'
            } | Set-Content $eventsPath
            Write-Host "  ✓ Renamed 'Event Description' to 'Event_Description'" -ForegroundColor Green
        }
        elseif ($cols -contains 'description') {
            Rename-Item $eventsPath "oil_events_backup.csv" -ErrorAction SilentlyContinue
            Get-Content "oil_events_backup.csv" | ForEach-Object {
                $_ -replace 'description', 'Event_Description' `
                   -replace 'date', 'Date' `
                   -replace 'category', 'Category'
            } | Set-Content $eventsPath
            Write-Host "  ✓ Renamed 'description' to 'Event_Description'" -ForegroundColor Green
        }
        else {
            Write-Host "  ✗ Cannot identify column names. Creating standard events file..." -ForegroundColor Red
            $eventsContent = @"
Date,Event_Description,Category
2012-07-01,EU embargo on Iranian oil imports due to nuclear program sanctions,Geopolitical/Sanctions
2014-11-27,OPEC decides not to cut production amid US shale boom,OPEC
2015-07-14,Iran nuclear deal (JCPOA) signed, leading to sanctions relief,Geopolitical
2016-11-30,OPEC agrees to first production cut in 8 years,OPEC
2018-05-08,US withdraws from Iran nuclear deal and reimposes sanctions,Geopolitical/Sanctions
2019-09-14,Drone attacks on Saudi Aramco facilities,Geopolitical/Conflict
2020-03-06,OPEC+ price war begins after failed agreement,OPEC/Economic
2020-03-11,WHO declares COVID-19 pandemic,Economic
2020-04-12,OPEC+ agrees to record production cuts,OPEC
2021-03-23,Suez Canal blocked by Ever Given,Geopolitical/Logistics
2022-02-24,Russia invades Ukraine,Geopolitical/Conflict
2022-03-08,US and allies impose bans on Russian oil imports,Geopolitical/Sanctions
2022-06-02,OPEC+ agrees to accelerate production increases,OPEC
"@
            $eventsContent | Set-Content $eventsPath
            Write-Host "  ✓ Created standard events file" -ForegroundColor Green
        }
    }
} else {
    Write-Host "⚠ Events file not found. Creating one..." -ForegroundColor Yellow
    $eventsContent = @"
Date,Event_Description,Category
2012-07-01,EU embargo on Iranian oil imports due to nuclear program sanctions,Geopolitical/Sanctions
2014-11-27,OPEC decides not to cut production amid US shale boom,OPEC
2015-07-14,Iran nuclear deal (JCPOA) signed, leading to sanctions relief,Geopolitical
2016-11-30,OPEC agrees to first production cut in 8 years,OPEC
2018-05-08,US withdraws from Iran nuclear deal and reimposes sanctions,Geopolitical/Sanctions
2019-09-14,Drone attacks on Saudi Aramco facilities,Geopolitical/Conflict
2020-03-06,OPEC+ price war begins after failed agreement,OPEC/Economic
2020-03-11,WHO declares COVID-19 pandemic,Economic
2020-04-12,OPEC+ agrees to record production cuts,OPEC
2021-03-23,Suez Canal blocked by Ever Given,Geopolitical/Logistics
2022-02-24,Russia invades Ukraine,Geopolitical/Conflict
2022-03-08,US and allies impose bans on Russian oil imports,Geopolitical/Sanctions
2022-06-02,OPEC+ agrees to accelerate production increases,OPEC
"@
    $eventsContent | Set-Content $eventsPath
    Write-Host "✓ Created events file at $eventsPath" -ForegroundColor Green
}

# 3. Fix the sample data creation in app.py
Write-Host "`n🔧 Fixing sample data function in app.py..." -ForegroundColor Cyan
$appPyPath = "app\backend\app.py"
if (Test-Path $appPyPath) {
    $content = Get-Content $appPyPath -Raw
    
    # Replace the broken create_sample_data function
    $fixedFunction = @'
def create_sample_data():
    """Create sample data for demo purposes"""
    global oil_df, events_df
    
    print("Creating sample data for demo...")
    
    # Sample price data
    dates = pd.date_range('2020-01-01', '2022-12-31', freq='D')
    np.random.seed(42)
    
    # Create trending data with volatility
    base_trend = np.linspace(40, 100, len(dates))
    noise = np.random.normal(0, 5, len(dates))
    prices = base_trend + noise
    
    oil_df = pd.DataFrame({
        'Date': dates,
        'Price': prices,
        'log_price': np.log(prices),
        'log_returns': pd.Series(np.log(prices)).diff(),
        'rolling_std_30': pd.Series(np.log(prices)).diff().rolling(30).std()
    })
    oil_df.set_index('Date', inplace=True)
    
    # Sample events
    events_data = {
        'Date': pd.to_datetime(['2020-03-11', '2021-03-23', '2022-02-24']),
        'Event_Description': [
            'COVID-19 pandemic declared',
            'Suez Canal blockage',
            'Russia invades Ukraine'
        ],
        'Category': ['Economic', 'Logistics', 'Conflict']
    }
    events_df = pd.DataFrame(events_data)
    
    # Save sample data
    os.makedirs('../../data/processed', exist_ok=True)
    oil_df.to_csv('../../data/processed_oil_prices.csv')
    events_df.to_csv('../../data/processed_events.csv', index=False)
    
    print("✓ Sample data created and saved")
'@
    
    # Use regex to replace the existing function
    if ($content -match 'def create_sample_data\(\):.*?(?=\n\S|\Z)') {
        $content = $content -replace $matches[0], $fixedFunction
        $content | Set-Content $appPyPath
        Write-Host "✓ Updated create_sample_data function in app.py" -ForegroundColor Green
    } else {
        Write-Host "⚠ Could not find function to replace. Appending fixed function..." -ForegroundColor Yellow
        Add-Content $appPyPath "`n$fixedFunction"
    }
} else {
    Write-Host "✗ app.py not found at $appPyPath" -ForegroundColor Red
}

# 4. Fix the data_prep.py column access
Write-Host "`n🔧 Fixing data_prep.py to handle column names..." -ForegroundColor Cyan
$dataPrepPath = "src\data_prep.py"
if (Test-Path $dataPrepPath) {
    $content = Get-Content $dataPrepPath -Raw
    
    # Replace hardcoded column names with dynamic detection
    $fixedMerge = @'
    for _, event in events_df.iterrows():
        # Find closest trading day to event date
        if 'Date' in event:
            event_date = event['Date']
        else:
            # Try alternative column names
            date_cols = [col for col in events_df.columns if 'date' in col.lower()]
            if date_cols:
                event_date = event[date_cols[0]]
            else:
                continue
                
        # Get event description
        if 'Event_Description' in event:
            desc = event['Event_Description']
        else:
            desc_cols = [col for col in events_df.columns if 'description' in col.lower() or 'desc' in col.lower()]
            if desc_cols:
                desc = event[desc_cols[0]]
            else:
                desc = ''
                
        # Get category
        if 'Category' in event:
            cat = event['Category']
        else:
            cat_cols = [col for col in events_df.columns if 'category' in col.lower() or 'cat' in col.lower()]
            if cat_cols:
                cat = event[cat_cols[0]]
            else:
                cat = ''
        
        closest_date = oil_df.index[oil_df.index.get_indexer([event_date], method='nearest')[0]]
        if closest_date in merged_df.index:
            merged_df.loc[closest_date, 'event'] = 1
            merged_df.loc[closest_date, 'event_description'] = desc
            merged_df.loc[closest_date, 'event_category'] = cat
'@
    
    # Replace the old for loop section
    if ($content -match 'for _, event in events_df\.iterrows\(\):.*?(?=\n\s*\n|\Z)') {
        $content = $content -replace $matches[0], $fixedMerge
        $content | Set-Content $dataPrepPath
        Write-Host "✓ Updated data_prep.py with flexible column handling" -ForegroundColor Green
    } else {
        Write-Host "⚠ Could not find the exact loop pattern. Manual check may be needed." -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ data_prep.py not found at $dataPrepPath" -ForegroundColor Red
}

# 5. Create a minimal Brent price CSV if not exists
$brentPath = r"C:\Users\hp\Pictures\brent-change-point\brent-change-point\data\raw\BrentOilPrices.csv"
if (-not (Test-Path $brentPath)) {
    Write-Host "`n⚠ Creating sample Brent price data..." -ForegroundColor Yellow
    $samplePrices = @"
Date,Price
2020-01-01,67.77
2020-01-02,68.12
2020-01-03,68.45
2020-01-04,68.30
2020-01-05,67.90
2020-01-06,67.50
2020-01-07,67.80
2020-01-08,68.00
2020-01-09,68.25
2020-01-10,68.50
"@
    $samplePrices | Set-Content $brentPath
    Write-Host "✓ Created sample Brent price file at $brentPath" -ForegroundColor Green
}

Write-Host "`n" + "=" * 60
Write-Host "✅ Setup fixes applied!" -ForegroundColor Green
Write-Host "Now run your Flask app again." -ForegroundColor Cyan
Write-Host "=" * 60
