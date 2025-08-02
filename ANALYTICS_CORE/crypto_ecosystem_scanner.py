# -*- coding: utf-8 -*-
# ==============================================================================
# == PEMINDAI EKOSISTEM KRIPTO vFinal - PROJECT CHIMERA ==
# ==============================================================================
#
# Lokasi: ANALYTICS_CORE/crypto_ecosystem_scanner.py
# Deskripsi: Memindai dan menganalisis ekosistem kripto berdasarkan daftar koin
#            yang didefinisikan secara internal, memprioritaskan berdasarkan
#            volume & katalis, dan menyesuaikan analisis berdasarkan kategori.
#            Dirancang untuk berjalan mandiri di VS Code tanpa file CSV eksternal.
#
# ==============================================================================
import logging
import random # Untuk simulasi data
import time # Untuk simulasi jitter API
from datetime import datetime

# --- PENYESUAIAN PATH DINAMIS (SEPATI DARI PINDAH PINDAH PINDAH.txt) ---
# Ini diasumsikan sudah ditangani di tingkat orkestrator
# --- AKHIR PENYESUAIAN PATH ---

# --- DATA KOIN INTERNAL (Menggantikan file CSV) ---
# Data ini diambil dan disintesis dari file CSV dan PDF yang Anda lampirkan.
INTERNAL_COIN_LIST = [
    # --- Dari PDF (Top 250?) ---
    {"simbol": "BTC", "nama_lengkap": "Bitcoin", "kategori": "Lapis 1 / Store of Value", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Institusional adoption, ETF inflows"},
    {"simbol": "ETH", "nama_lengkap": "Ethereum", "kategori": "Lapis 1 / Smart Contracts", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "EIP implementation, DeFi growth"},
    {"simbol": "BNB", "nama_lengkap": "Binance Coin", "kategori": "Exchange Token / Lapis 1", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Binance ecosystem expansion, burns"},
    {"simbol": "SOL", "nama_lengkap": "Solana", "kategori": "Lapis 1 / Smart Contracts", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "NFT resurgence, DeFi partnerships"},
    {"simbol": "XRP", "nama_lengkap": "XRP", "kategori": "Payments", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Legal resolution, cross-border payments"},
    {"simbol": "DOGE", "nama_lengkap": "Dogecoin", "kategori": "Memecoin", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Meme trends, celebrity tweets"},
    {"simbol": "TON", "nama_lengkap": "Toncoin", "kategori": "Lapis 1 / Messaging", "volume_perdagangan": "Tinggi", "potensi_katalis": "Telegram integration, user growth"},
    {"simbol": "ADA", "nama_lengkap": "Cardano", "kategori": "Lapis 1 / Smart Contracts", "volume_perdagangan": "Tinggi", "potensi_katalis": "Smart contract adoption, Africa expansion"},
    {"simbol": "SHIB", "nama_lengkap": "Shiba Inu", "kategori": "Memecoin", "volume_perdagangan": "Tinggi", "potensi_katalis": "Meme popularity, Shibarium development"},
    {"simbol": "AVAX", "nama_lengkap": "Avalanche", "kategori": "Lapis 1 / Smart Contracts", "volume_perdagangan": "Tinggi", "potensi_katalis": "Subnet growth, institutional DeFi"},
    {"simbol": "TRX", "nama_lengkap": "TRON", "kategori": "Lapis 1 / Content", "volume_perdagangan": "Tinggi", "potensi_katalis": "Entertainment partnerships, stablecoin usage"},
    {"simbol": "DOT", "nama_lengkap": "Polkadot", "kategori": "Layer 0 / Interoperability", "volume_perdagangan": "Tinggi", "potensi_katalis": "Parachain auctions, interoperability news"},
    {"simbol": "LINK", "nama_lengkap": "Chainlink", "kategori": "Oracle", "volume_perdagangan": "Tinggi", "potensi_katalis": "DeFi oracle demand, new data feeds"},
    {"simbol": "BCH", "nama_lengkap": "Bitcoin Cash", "kategori": "Payments / Fork", "volume_perdagangan": "Tinggi", "potensi_katalis": "Halving cycle, merchant adoption"},
    {"simbol": "NEAR", "nama_lengkap": "NEAR Protocol", "kategori": "Lapis 1 / Sharding", "volume_perdagangan": "Tinggi", "potensi_katalis": "Ecosystem growth, developer grants"},
    {"simbol": "MATIC", "nama_lengkap": "Polygon", "kategori": "Lapis 2 / Scaling", "volume_perdagangan": "Tinggi", "potensi_katalis": "Ethereum gas wars, zkEVM adoption"},
    {"simbol": "LTC", "nama_lengkap": "Litecoin", "kategori": "Payments", "volume_perdagangan": "Tinggi", "potensi_katalis": "Merchant adoption, halving"},
    {"simbol": "ICP", "nama_lengkap": "Internet Computer", "kategori": "Decentralized Cloud", "volume_perdagangan": "Tinggi", "potensi_katalis": "Smart contract updates, internet identity"},
    {"simbol": "LEO", "nama_lengkap": "LEO Token", "kategori": "Exchange Token", "volume_perdagangan": "Tinggi", "potensi_katalis": "Bitfinex activity, token burns"},
    {"simbol": "KAS", "nama_lengkap": "Kaspa", "kategori": "Lapis 1 / PoW", "volume_perdagangan": "Tinggi", "potensi_katalis": "ASIC mining, DAG innovation"},
    {"simbol": "FTM", "nama_lengkap": "Fantom", "kategori": "Lapis 1 / DAG", "volume_perdagangan": "Tinggi", "potensi_katalis": "DeFi TVL, Opera upgrade"},
    {"simbol": "ETC", "nama_lengkap": "Ethereum Classic", "kategori": "Lapis 1 / Smart Contracts", "volume_perdagangan": "Tinggi", "potensi_katalis": "51% attack fears, classic narrative"},
    {"simbol": "APT", "nama_lengkap": "Aptos", "kategori": "Lapis 1 / Move", "volume_perdagangan": "Tinggi", "potensi_katalis": "Move language adoption, ecosystem grants"},
    {"simbol": "HBAR", "nama_lengkap": "Hedera", "kategori": "DLT / Enterprise", "volume_perdagangan": "Tinggi", "potensi_katalis": "Governance council news, enterprise partnerships"},
    {"simbol": "ATOM", "nama_lengkap": "Cosmos", "kategori": "Layer 0 / Interoperability", "volume_perdagangan": "Tinggi", "potensi_katalis": "IBC bridge activity, hub upgrades"},
    {"simbol": "ARB", "nama_lengkap": "Arbitrum", "kategori": "Lapis 2 / Rollup", "volume_perdagangan": "Tinggi", "potensi_katalis": "Arbitrum Odyssey, ecosystem growth"},
    {"simbol": "RNDR", "nama_lengkap": "Render", "kategori": "AI / DePIN", "volume_perdagangan": "Tinggi", "potensi_katalis": "AI rendering demand, Nvidia partnerships"},
    {"simbol": "FIL", "nama_lengkap": "Filecoin", "kategori": "Decentralized Storage", "volume_perdagangan": "Tinggi", "potensi_katalis": "NFT storage demand, Filecoin Plus"},
    {"simbol": "SUI", "nama_lengkap": "Sui", "kategori": "Lapis 1 / Move", "volume_perdagangan": "Tinggi", "potensi_katalis": "Move language, parallel execution"},
    {"simbol": "PEPE", "nama_lengkap": "Pepe", "kategori": "Memecoin", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Meme virality, exchange listings"},
    {"simbol": "WIF", "nama_lengkap": "dogwifhat", "kategori": "Memecoin", "volume_perdagangan": "Tinggi", "potensi_katalis": "Meme culture, Solana ecosystem"},
    {"simbol": "NOT", "nama_lengkap": "Notcoin", "kategori": "Gaming / Telegram", "volume_perdagangan": "Tinggi", "potensi_katalis": "Airdrop claims, Telegram mini-apps"},
    {"simbol": "OP", "nama_lengkap": "Optimism", "kategori": "Lapis 2 / Rollup", "volume_perdagangan": "Tinggi", "potensi_katalis": "OP token airdrops, Superchain vision"},
    {"simbol": "TAO", "nama_lengkap": "Bittensor", "kategori": "AI / Decentralized ML", "volume_perdagangan": "Tinggi", "potensi_katalis": "AI breakthroughs, network mining activity"},
    {"simbol": "UNI", "nama_lengkap": "Uniswap", "kategori": "DeFi / DEX", "volume_perdagangan": "Tinggi", "potensi_katalis": "Governance votes, fee switch"},
    {"simbol": "INJ", "nama_lengkap": "Injective", "kategori": "Lapis 1 / DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "Derivatives trading demand, cosmos integration"},
    {"simbol": "GRT", "nama_lengkap": "The Graph", "kategori": "Indexing / Web3", "volume_perdagangan": "Tinggi", "potensi_katalis": "Query demand, subgraph launches"},
    {"simbol": "VET", "nama_lengkap": "VeChain", "kategori": "Supply Chain", "volume_perdagangan": "Tinggi", "potensi_katalis": "Corporate partnerships, supply chain adoption"},
    {"simbol": "AAVE", "nama_lengkap": "Aave", "kategori": "DeFi / Lending", "volume_perdagangan": "Tinggi", "potensi_katalis": "Liquidity mining, new asset listings"},
    {"simbol": "SEI", "nama_lengkap": "Sei", "kategori": "Lapis 1 / Trading", "volume_perdagangan": "Tinggi", "potensi_katalis": "DEX volume, orderbook innovations"},
    {"simbol": "MKR", "nama_lengkap": "Maker", "kategori": "DeFi / Stablecoin", "volume_perdagangan": "Tinggi", "potensi_katalis": "DAI stability fees, governance votes"},
    {"simbol": "TIA", "nama_lengkap": "Celestia", "kategori": "Modular / Data Availability", "volume_perdagangan": "Tinggi", "potensi_katalis": "Modular blockchain trends, rollup adoption"},
    {"simbol": "ONDO", "nama_lengkap": "Ondo", "kategori": "Real World Assets (RWA)", "volume_perdagangan": "Tinggi", "potensi_katalis": "RWA tokenization, institutional interest"},
    {"simbol": "STX", "nama_lengkap": "Stacks", "kategori": "Bitcoin Layer 2", "volume_perdagangan": "Tinggi", "potensi_katalis": "Bitcoin NFT activity, sBTC development"},
    {"simbol": "LDO", "nama_lengkap": "Lido DAO", "kategori": "Liquid Staking", "volume_perdagangan": "Tinggi", "potensi_katalis": "stETH depegging fears, L2 expansion"},
    {"simbol": "FET", "nama_lengkap": "Fetch.ai", "kategori": "AI / Agents", "volume_perdagangan": "Sedang", "potensi_katalis": "AI agent partnerships, data marketplace"},
    {"simbol": "ENA", "nama_lengkap": "Ethena", "kategori": "DeFi / Synthetic Dollar", "volume_perdagangan": "Tinggi", "potensi_katalis": "USTC recovery narrative, yield dynamics"},
    {"simbol": "GALA", "nama_lengkap": "Gala", "kategori": "Gaming / Metaverse", "volume_perdagangan": "Tinggi", "potensi_katalis": "Game launches, GalaChain adoption"},
    {"simbol": "BONK", "nama_lengkap": "Bonk", "kategori": "Memecoin", "volume_perdagangan": "Tinggi", "potensi_katalis": "Solana memecoin trend, community growth"},
    {"simbol": "BEAM", "nama_lengkap": "Beam", "kategori": "Gaming / Privacy", "volume_perdagangan": "Sedang", "potensi_katalis": "Privacy tech, gaming integrations"},
    {"simbol": "JUP", "nama_lengkap": "Jupiter", "kategori": "DeFi / DEX Aggregator", "volume_perdagangan": "Tinggi", "potensi_katalis": "Solana DEX volume, new route optimization"},
    {"simbol": "ALGO", "nama_lengkap": "Algorand", "kategori": "Lapis 1 / Pure PoS", "volume_perdagangan": "Sedang", "potensi_katalis": "Governance rewards, Algorand Foundation grants"},
    {"simbol": "RUNE", "nama_lengkap": "THORChain", "kategori": "DeFi / Cross-chain", "volume_perdagangan": "Tinggi", "potensi_katalis": "Liquidity depth, cross-chain swaps"},
    {"simbol": "AGIX", "nama_lengkap": "SingularityNET", "kategori": "AI / Marketplace", "volume_perdagangan": "Sedang", "potensi_katalis": "AI breakthroughs, platform growth"},
    {"simbol": "PENDLE", "nama_lengkap": "Pendle", "kategori": "DeFi / Yield Trading", "volume_perdagangan": "Tinggi", "potensi_katalis": "Yield trading demand, pt yt innovations"},
    {"simbol": "FTT", "nama_lengkap": "FTX Token", "kategori": "Exchange Token", "volume_perdagangan": "Rendah", "potensi_katalis": "FTX news, community forks"},
    {"simbol": "SAND", "nama_lengkap": "The Sandbox", "kategori": "Metaverse", "volume_perdagangan": "Tinggi", "potensi_katalis": "Celebrity partnerships, land sales"},
    {"simbol": "AXS", "nama_lengkap": "Axie Infinity", "kategori": "Gaming / Metaverse", "volume_perdagangan": "Tinggi", "potensi_katalis": "Scholarship demand, token unlocks"},
    {"simbol": "EGLD", "nama_lengkap": "MultiversX (ex-Elrond)", "kategori": "Lapis 1 / Sharding", "volume_perdagangan": "Sedang", "potensi_katalis": "Web3 mobile adoption, Maiar DEX"},
    {"simbol": "MANA", "nama_lengkap": "Decentraland", "kategori": "Metaverse", "volume_perdagangan": "Sedang", "potensi_katalis": "Virtual land sales, metaverse events"},
    {"simbol": "DYDX", "nama_lengkap": "dYdX", "kategori": "DeFi / DEX", "volume_perdagangan": "Tinggi", "potensi_katalis": "Perpetual trading, v4 launch"},
    {"simbol": "FLOW", "nama_lengkap": "Flow", "kategori": "Lapis 1 / NFTs", "volume_perdagangan": "Sedang", "potensi_katalis": "NBA Top Shot activity, Dapper Wallet"},
    {"simbol": "ORDI", "nama_lengkap": "Ordi", "kategori": "BRC-20 / Memecoin", "volume_perdagangan": "Tinggi", "potensi_katalis": "Ordinal NFTs, Bitcoin ecosystem"},
    {"simbol": "SNX", "nama_lengkap": "Synthetix", "kategori": "DeFi / Derivatives", "volume_perdagangan": "Sedang", "potensi_katalis": "Synthetic asset demand, Kwenta growth"},
    {"simbol": "GNO", "nama_lengkap": "Gnosis", "kategori": "Infrastructure / DAO", "volume_perdagangan": "Sedang", "potensi_katalis": "DAO tools, prediction markets"},
    {"simbol": "ZETA", "nama_lengkap": "ZetaChain", "kategori": "Lapis 1 / Interoperability", "volume_perdagangan": "Sedang", "potensi_katalis": "Cosmos integration, omnichain contracts"},
    {"simbol": "1000SATS", "nama_lengkap": "Sats", "kategori": "BRC-20 / Memecoin", "volume_perdagangan": "Tinggi", "potensi_katalis": "BRC-20 trend, Bitcoin meme"},
    {"simbol": "AXL", "nama_lengkap": "Axelar", "kategori": "Interoperability", "volume_perdagangan": "Sedang", "potensi_katalis": "Cross-chain dApp adoption, validator growth"},
    {"simbol": "MINA", "nama_lengkap": "Mina Protocol", "kategori": "Lapis 1 / ZK", "volume_perdagangan": "Sedang", "potensi_katalis": "ZK tech, o(1) Labs grants"},
    {"simbol": "AR", "nama_lengkap": "Arweave", "kategori": "Decentralized Storage", "volume_perdagangan": "Sedang", "potensi_katalis": "Permanent web, permaweb apps"},
    {"simbol": "WLD", "nama_lengkap": "Worldcoin", "kategori": "Identity", "volume_perdagangan": "Sedang", "potensi_katalis": "Orb deployment, privacy debates"},
    {"simbol": "XMR", "nama_lengkap": "Monero", "kategori": "Privacy", "volume_perdagangan": "Sedang", "potensi_katalis": "Privacy coin regulation, fungibility"},
    {"simbol": "WOO", "nama_lengkap": "WOO Network", "kategori": "Liquidity / CeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "Institutional inflow, WOO X exchange"},
    {"simbol": "CRV", "nama_lengkap": "Curve DAO Token", "kategori": "DeFi / DEX", "volume_perdagangan": "Tinggi", "potensi_katalis": "Pool gauge wars, crvUSD adoption"},
    {"simbol": "KSM", "nama_lengkap": "Kusama", "kategori": "Layer 0 / Canary Network", "volume_perdagangan": "Sedang", "potensi_katalis": "Polkadot parachain auctions, canary network"},
    {"simbol": "CAKE", "nama_lengkap": "PancakeSwap", "kategori": "DeFi / DEX", "volume_perdagangan": "Tinggi", "potensi_katalis": "IFO launches, BSC ecosystem"},
    {"simbol": "ZIL", "nama_lengkap": "Zilliqa", "kategori": "Lapis 1 / Sharding", "volume_perdagangan": "Rendah", "potensi_katalis": "Sharding tech, ZIL staking"},
    {"simbol": "NEO", "nama_lengkap": "Neo", "kategori": "Lapis 1 / Smart Contracts", "volume_perdagangan": "Rendah", "potensi_katalis": "Neo N3 upgrade, China regulation"},
    {"simbol": "OCEAN", "nama_lengkap": "Ocean Protocol", "kategori": "AI / Data Marketplace", "volume_perdagangan": "Sedang", "potensi_katalis": "Data marketplace activity, AI data demand"},
    {"simbol": "ENS", "nama_lengkap": "Ethereum Name Service", "kategori": "Naming Service", "volume_perdagangan": "Sedang", "potensi_katalis": "Web3 identity, .eth adoption"},
    {"simbol": "DYM", "nama_lengkap": "Dymension", "kategori": "Modular / RollApps", "volume_perdagangan": "Sedang", "potensi_katalis": "RollApp launches, modular blockchain trends"},
    {"simbol": "WAVES", "nama_lengkap": "Waves", "kategori": "Lapis 1 / Platform", "volume_perdagangan": "Rendah", "potensi_katalis": "Waves Enterprise, token issuance"},
    {"simbol": "FXS", "nama_lengkap": "Frax Share", "kategori": "DeFi / Stablecoin", "volume_perdagangan": "Sedang", "potensi_katalis": "Frax ecosystem, AMO growth"},
    {"simbol": "GMX", "nama_lengkap": "GMX", "kategori": "DeFi / DEX", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "BTC/ETH volatility, GLP composition"},
    {"simbol": "COMP", "nama_lengkap": "Compound", "kategori": "DeFi / Lending", "volume_perdagangan": "Sedang", "potensi_katalis": "Governance proposals, interest rate changes"},
    {"simbol": "ROSE", "nama_lengkap": "Oasis Network", "kategori": "Lapis 1 / Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "DeFi privacy demand, ParaTime adoption"},
    {"simbol": "GMT", "nama_lengkap": "STEPN", "kategori": "Move-to-Earn", "volume_perdagangan": "Sedang", "potensi_katalis": "Web3 fitness, sneaker marketplace"},
    {"simbol": "IO", "nama_lengkap": "IO.NET", "kategori": "AI / DePIN", "volume_perdagangan": "Sedang", "potensi_katalis": "AI computing, distributed GPU"},
    {"simbol": "MAV", "nama_lengkap": "Maverick Protocol", "kategori": "DeFi / DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "Concentrated liquidity, Maverick 2.0"},
    {"simbol": "ZEC", "nama_lengkap": "Zcash", "kategori": "Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "Halving events, privacy coin regulation"},
    {"simbol": "1INCH", "nama_lengkap": "1inch Network", "kategori": "DeFi / DEX Aggregator", "volume_perdagangan": "Tinggi", "potensi_katalis": "Route optimization, limit orders"},
    {"simbol": "BLUR", "nama_lengkap": "Blur", "kategori": "NFT Marketplace", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT trading wars, airdrops"},
    {"simbol": "CVX", "nama_lengkap": "Convex Finance", "kategori": "DeFi / Yield", "volume_perdagangan": "Sedang", "potensi_katalis": "CRV boosting, Convex yield"},
    {"simbol": "ILV", "nama_lengkap": "Illuvium", "kategori": "Gaming", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT game drops, Illuvium 2"},
    {"simbol": "IOTA", "nama_lengkap": "IOTA", "kategori": "IoT / Tangle", "volume_perdagangan": "Rendah", "potensi_katalis": "Industry 4.0, Smart cities"},
    {"simbol": "APE", "nama_lengkap": "ApeCoin", "kategori": "Metaverse / DAO", "volume_perdagangan": "Sedang", "potensi_katalis": "ApeCoin DAO, Otherside metaverse"},
    {"simbol": "PYTH", "nama_lengkap": "Pyth Network", "kategori": "Oracle", "volume_perdagangan": "Tinggi", "potensi_katalis": "DeFi oracle demand, publisher growth"},
    {"simbol": "GTC", "nama_lengkap": "Gitcoin", "kategori": "Public Goods Funding", "volume_perdagangan": "Sedang", "potensi_katalis": "Grants rounds, quadratic funding"},
    {"simbol": "KAVA", "nama_lengkap": "Kava", "kategori": "Lapis 1 / Interoperability", "volume_perdagangan": "Sedang", "potensi_katalis": "Multi-chain DeFi integrations, CDP growth"},
    {"simbol": "MNT", "nama_lengkap": "Mantle", "kategori": "Lapis 2", "volume_perdagangan": "Sedang", "potensi_katalis": "Modular chain, EigenLayer"},
    {"simbol": "MASK", "nama_lengkap": "Mask Network", "kategori": "Web3 / SocialFi", "volume_perdagangan": "Rendah", "potensi_katalis": "Social media integration, web3 portal"},
    {"simbol": "ANKR", "nama_lengkap": "Ankr", "kategori": "DePIN / Infrastructure", "volume_perdagangan": "Sedang", "potensi_katalis": "RPC endpoints, staking services"},
    {"simbol": "QTUM", "nama_lengkap": "Qtum", "kategori": "Lapis 1 / Smart Contracts", "volume_perdagangan": "Rendah", "potensi_katalis": "Smart contract updates, Qtum Qt"},
    {"simbol": "IMX", "nama_lengkap": "Immutable", "kategori": "Lapis 2 / Gaming& NFTs", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT game launches, zkEVM adoption"},
    {"simbol": "AUDIO", "nama_lengkap": "Audius", "kategori": "Web3 / Music", "volume_perdagangan": "Sedang", "potensi_katalis": "Artist migrations, music NFTs"},
    {"simbol": "BAT", "nama_lengkap": "Basic Attention Token", "kategori": "Web3 / Advertising", "volume_perdagangan": "Rendah", "potensi_katalis": "Brave browser growth, ad revenue"},
    {"simbol": "LRC", "nama_lengkap": "Loopring", "kategori": "Lapis 2 / ZK-Rollup", "volume_perdagangan": "Sedang", "potensi_katalis": "ZK-Rollup adoption, Loopring DEX"},
    {"simbol": "RVN", "nama_lengkap": "Ravencoin", "kategori": "Asset Tokenization", "volume_perdagangan": "Sedang", "potensi_katalis": "Asset issuance, meme coin launches"},
    {"simbol": "HOT", "nama_lengkap": "Holo", "kategori": "Decentralized Cloud", "volume_perdagangan": "Rendah", "potensi_katalis": "Holo hosting, distributed cloud"},
    {"simbol": "ENJ", "nama_lengkap": "Enjin Coin", "kategori": "Gaming / NFTs", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT collaborations, Enjin Matrixchain"},
    {"simbol": "FLUX", "nama_lengkap": "Flux", "kategori": "DePIN / Cloud", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized cloud, node operator demand"},
    {"simbol": "CELO", "nama_lengkap": "Celo", "kategori": "Lapis 1 / Payments", "volume_perdagangan": "Rendah", "potensi_katalis": "Mobile payment adoption, cUSD stability"},
    {"simbol": "ZRX", "nama_lengkap": "0x Protocol", "kategori": "DeFi / DEX Infrastructure", "volume_perdagangan": "Rendah", "potensi_katalis": "DEX aggregator integration, NFT trades"},
    {"simbol": "IOTX", "nama_lengkap": "IoTeX", "kategori": "DePIN / IoT", "volume_perdagangan": "Rendah", "potensi_katalis": "IoT device adoption, uCam privacy"},
    {"simbol": "YFI", "nama_lengkap": "yearn.finance", "kategori": "DeFi / Yield Aggregator", "volume_perdagangan": "Sedang", "potensi_katalis": "Andre Cronje tweets, vault strategies"},
    {"simbol": "UMA", "nama_lengkap": "UMA", "kategori": "DeFi / Oracles", "volume_perdagangan": "Rendah", "potensi_katalis": "Optimistic oracle usage, synthetic assets"},
    {"simbol": "SUSHI", "nama_lengkap": "SushiSwap", "kategori": "DeFi / DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "Onsen menu additions, Kashi lending"},
    {"simbol": "KNC", "nama_lengkap": "Kyber Network", "kategori": "DeFi / DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "Kyber DMM, DMM aggregates"},
    {"simbol": "REN", "nama_lengkap": "REN", "kategori": "Interoperability", "volume_perdagangan": "Rendah", "potensi_katalis": "Bridge usage, inter-chain liquidity"},
    {"simbol": "TRB", "nama_lengkap": "Tellor", "kategori": "Oracle", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized oracle demand, data requests"},
    {"simbol": "BAND", "nama_lengkap": "Band Protocol", "kategori": "Oracle", "volume_perdagangan": "Sedang", "potensi_katalis": "Cross-chain data demand, oracle partnerships"},
    {"simbol": "BAL", "nama_lengkap": "Balancer", "kategori": "DeFi / DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "veBAL emissions, portfolio management"},
    {"simbol": "STORJ", "nama_lengkap": "Storj", "kategori": "Decentralized Storage", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized storage demand, Tardigrade"},
    {"simbol": "CELR", "nama_lengkap": "Celer Network", "kategori": "Lapis 2 / Interop", "volume_perdagangan": "Rendah", "potensi_katalis": "cBridge, layer2.finance"},
    {"simbol": "SKL", "nama_lengkap": "SKALE Network", "kategori": "Lapis 2 / Elastic Chains", "volume_perdagangan": "Sedang", "potensi_katalis": "Ethereum scaling demand, SKALE chains"},
    {"simbol": "MANTA", "nama_lengkap": "Manta Network", "kategori": "Modular / Zero-Knowledge", "volume_perdagangan": "Sedang", "potensi_katalis": "ZK privacy, native ZK rollups"},
    {"simbol": "DASH", "nama_lengkap": "Dash", "kategori": "Payments / Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "Merchant adoption, masternode rewards"},
    {"simbol": "API3", "nama_lengkap": "API3", "kategori": "Oracle", "volume_perdagangan": "Sedang", "potensi_katalis": "dAPI adoption by DeFi, API provider growth"},
    {"simbol": "MYRO", "nama_lengkap": "Myro", "kategori": "Memecoin (Solana)", "volume_perdagangan": "Rendah", "potensi_katalis": "Meme potential, community building"},
    {"simbol": "IOST", "nama_lengkap": "IOST", "kategori": "Lapis 1 / Enterprise", "volume_perdagangan": "Rendah", "potensi_katalis": "Enterprise blockchain demand, Binance listing"},
    {"simbol": "HIGH", "nama_lengkap": "Highstreet", "kategori": "Metaverse / Commerce", "volume_perdagangan": "Rendah", "potensi_katalis": "Metaverse events, virtual real estate"},
    {"simbol": "ARPA", "nama_lengkap": "ARPA Computation Network", "kategori": "Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "MPC protocol updates, privacy computing"},
    {"simbol": "DUSK", "nama_lengkap": "Dusk", "kategori": "Lapis 1 / Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "Securities tokenization, PLONK zk-SNARKs"},
    {"simbol": "NTRN", "nama_lengkap": "Neutron", "kategori": "Smart Contracts / Cosmos", "volume_perdagangan": "Rendah", "potensi_katalis": "Cosmos smart contracts, interchain queries"},
    {"simbol": "CKB", "nama_lengkap": "Nervos Network", "kategori": "Lapis 1 / Interop", "volume_perdagangan": "Rendah", "potensi_katalis": "Bitcoin layer 2 demand, Nervos DAO"},
    {"simbol": "CFX", "nama_lengkap": "Conflux", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Tree-graph consensus, Chinese market"},
    {"simbol": "LINA", "nama_lengkap": "Linear Finance", "kategori": "DeFi / Derivatives", "volume_perdagangan": "Rendah", "potensi_katalis": "Cross-chain DeFi, LINA staking"},
    {"simbol": "MAGIC", "nama_lengkap": "Magic", "kategori": "Gaming / TreasureDAO", "volume_perdagangan": "Rendah", "potensi_katalis": "Treasure ecosystem, memeland NFTs"},
    {"simbol": "SXP", "nama_lengkap": "Swipe", "kategori": "Payments (Acquired by Binance)", "volume_perdagangan": "Rendah", "potensi_katalis": "Crypto card adoption, Binance support"},
    {"simbol": "CTK", "nama_lengkap": "CertiK", "kategori": "Security", "volume_perdagangan": "Rendah", "potensi_katalis": "Smart contract audits, Skynet monitoring"},
    {"simbol": "HOOK", "nama_lengkap": "Hooked Protocol", "kategori": "Web3 / Ed-Tech", "volume_perdagangan": "Rendah", "potensi_katalis": "Web3 gamification, Hooked Verse"},
    {"simbol": "PERP", "nama_lengkap": "Perpetual Protocol", "kategori": "DeFi / DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "BTC/ETH volatility, vAMM innovation"},
    {"simbol": "ID", "nama_lengkap": "SPACE ID", "kategori": "Identity / Naming", "volume_perdagangan": "Rendah", "potensi_katalis": "Web3 identity, BNB domain names"},
    {"simbol": "LQTY", "nama_lengkap": "Liquity", "kategori": "DeFi / Stablecoin", "volume_perdagangan": "Rendah", "potensi_katalis": "LUSD stablecoin, trove liquidations"},
    {"simbol": "OMG", "nama_lengkap": "OMG Network", "kategori": "Lapis 2 / Payments", "volume_perdagangan": "Rendah", "potensi_katalis": "Ethereum scaling demand, OMG 2.0"},
    {"simbol": "AMB", "nama_lengkap": "AirDAO", "kategori": "Lapis 1 / DAO", "volume_perdagangan": "Rendah", "potensi_katalis": "DAO tools, ambrosus network"},
    {"simbol": "CHR", "nama_lengkap": "Chromia", "kategori": "Lapis 1 / Relational DB", "volume_perdagangan": "Rendah", "potensi_katalis": "Relational blockchain, Chromia dApps"},
    {"simbol": "EDU", "nama_lengkap": "Open Campus", "kategori": "Web3 / Ed-Tech", "volume_perdagangan": "Rendah", "potensi_katalis": "Education token, open campus dApps"},
    {"simbol": "COTI", "nama_lengkap": "COTI", "kategori": "Lapis 1 / DAG", "volume_perdagangan": "Rendah", "potensi_katalis": "DAG technology news, COTI Pay"},
    {"simbol": "LPT", "nama_lengkap": "Livepeer", "kategori": "DePIN / Video Streaming", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized video demand, video mining"},
    {"simbol": "LEVER", "nama_lengkap": "LeverFi", "kategori": "DeFi / Leverage Trading", "volume_perdagangan": "Rendah", "potensi_katalis": "Leverage yield farming, DeFi leverage"},
    {"simbol": "NKN", "nama_lengkap": "NKN", "kategori": "DePIN / Network", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized network demand, NKN mining"},
    {"simbol": "POWR", "nama_lengkap": "Powerledger", "kategori": "Energy Trading", "volume_perdagangan": "Rendah", "potensi_katalis": "Renewable energy trading, blockchain energy"},
    {"simbol": "DENT", "nama_lengkap": "DENT", "kategori": "Mobile Data", "volume_perdagangan": "Rendah", "potensi_katalis": "Mobile data marketplace, telecom partnerships"},
    {"simbol": "JOE", "nama_lengkap": "Joe", "kategori": "DeFi / DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "Trader Joe DEX, AVAX ecosystem"},
    {"simbol": "TLM", "nama_lengkap": "Alien Worlds", "kategori": "Gaming / Metaverse", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT drops, Trilium mining"},
    {"simbol": "AUCTION", "nama_lengkap": "Bounce Finance", "kategori": "DeFi / Auction", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT auctions, fixed swap"},
    {"simbol": "RAD", "nama_lengkap": "Radicle", "kategori": "Code Collaboration", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized code, git alternative"},
    {"simbol": "CYBER", "nama_lengkap": "CyberConnect", "kategori": "Web3 / SocialFi", "volume_perdagangan": "Rendah", "potensi_katalis": "Social graph adoption, web3 identity"},
    {"simbol": "ALPHA", "nama_lengkap": "Stella", "kategori": "DeFi / Lending", "volume_perdagangan": "Rendah", "potensi_katalis": "StellaSwap, Moonbeam ecosystem"},
    {"simbol": "XVS", "nama_lengkap": "Venus", "kategori": "DeFi / Lending", "volume_perdagangan": "Sedang", "potensi_katalis": "Binance Smart Chain activity, interest rates"},
    {"simbol": "OGN", "nama_lengkap": "Origin Protocol", "kategori": "DeFi / Yield", "volume_perdagangan": "Rendah", "potensi_katalis": "Origin Dollar, NFT marketplace"},
    {"simbol": "MEME", "nama_lengkap": "Memecoin", "kategori": "Memecoin / NFT", "volume_perdagangan": "Rendah", "potensi_katalis": "Meme culture, NFT community"},
    {"simbol": "STMX", "nama_lengkap": "StormX", "kategori": "Shopping Rewards", "volume_perdagangan": "Rendah", "potensi_katalis": "Shopping rewards, Storm Market"},
    {"simbol": "PEOPLE", "nama_lengkap": "ConstitutionDAO", "kategori": "DAO / Memecoin", "volume_perdagangan": "Rendah", "potensi_katalis": "DAO governance, constitution bid"},
    {"simbol": "BNX", "nama_lengkap": "BinaryX", "kategori": "Gaming", "volume_perdagangan": "Rendah", "potensi_katalis": "CyberDragon game, BNX tokenomics"},
    {"simbol": "BEL", "nama_lengkap": "Bella Protocol", "kategori": "DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "Single-sided liquidity, Bella DeFi"},
    {"simbol": "USDC", "nama_lengkap": "USD Coin", "kategori": "Stablecoin", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Regulatory clarity, DeFi liquidity"},
    {"simbol": "T", "nama_lengkap": "Threshold", "kategori": "Infrastructure / Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "tBTC, privacy infrastructure"},
    {"simbol": "RSR", "nama_lengkap": "Reserve Rights", "kategori": "DeFi / Stablecoin", "volume_perdagangan": "Rendah", "potensi_katalis": "RSV stablecoin adoption, reserve backing"},
    {"simbol": "BAKE", "nama_lengkap": "BakeryToken", "kategori": "DeFi / DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "BakerySwap, BSC ecosystem"},
    {"simbol": "LIT", "nama_lengkap": "Litentry", "kategori": "Identity", "volume_perdagangan": "Rendah", "potensi_katalis": "Cross-chain identity, credential API"},
    {"simbol": "GAL", "nama_lengkap": "Galxe", "kategori": "Web3 / Credentials", "volume_perdagangan": "Rendah", "potensi_katalis": "Web3 credentials, campaign management"},
    {"simbol": "USTC", "nama_lengkap": "TerraClassicUSD", "kategori": "Algorithmic Stablecoin", "volume_perdagangan": "Rendah", "potensi_katalis": "Luna 2.0, algorithmic peg"},
    {"simbol": "HFT", "nama_lengkap": "Hashflow", "kategori": "DeFi / DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "MEV protection demand, professional trading"},
    {"simbol": "FRONT", "nama_lengkap": "Frontier", "kategori": "DeFi Aggregator", "volume_perdagangan": "Rendah", "potensi_katalis": "DeFi aggregator, wallet integration"},
    {"simbol": "UNFI", "nama_lengkap": "Unifi Protocol DAO", "kategori": "DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "Multi-chain DeFi, UNFI tokenomics"},
    {"simbol": "BLZ", "nama_lengkap": "Bluzelle", "kategori": "Decentralized Storage", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized storage, oracle services"},
    {"simbol": "TRU", "nama_lengkap": "TrueFi", "kategori": "DeFi / Uncollateralized Lending", "volume_perdagangan": "Rendah", "potensi_katalis": "Uncollateralized lending, TRU staking"},
    {"simbol": "REEF", "nama_lengkap": "Reef", "kategori": "Lapis 1 / DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "DeFi yield optimizer, Reef Finance"},
    {"simbol": "KEY", "nama_lengkap": "SelfKey", "kategori": "Identity", "volume_perdagangan": "Rendah", "potensi_katalis": "Self-sovereign identity, KYC marketplace"},
    {"simbol": "DGB", "nama_lengkap": "DigiByte", "kategori": "UTXO / Payments", "volume_perdagangan": "Rendah", "potensi_katalis": "Merchant adoption, DigiShield"},
    {"simbol": "CVC", "nama_lengkap": "Civic", "kategori": "Identity", "volume_perdagangan": "Rendah", "potensi_katalis": "KYC/AML regulation news, identity verification"},
    {"simbol": "COMBO", "nama_lengkap": "Furucombo", "kategori": "DeFi Aggregator", "volume_perdagangan": "Rendah", "potensi_katalis": "DeFi lego blocks, transaction optimization"},
    {"simbol": "DODO", "nama_lengkap": "DODO", "kategori": "DeFi / DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "PMM algorithm, crowd pooling"},
    {"simbol": "ATA", "nama_lengkap": "Automata Network", "kategori": "Privacy / Middleware", "volume_perdagangan": "Rendah", "potensi_katalis": "Privacy middleware, bot detection"},
    {"simbol": "RDNT", "nama_lengkap": "Radiant Capital", "kategori": "DeFi / Lending", "volume_perdagangan": "Rendah", "potensi_katalis": "Interest rate changes, lending protocol"},
    {"simbol": "AGLD", "nama_lengkap": "Adventure Gold", "kategori": "Loot Project / NFT", "volume_perdagangan": "Rendah", "potensi_katalis": "Loot NFTs, adventure games"},
    {"simbol": "TOMO", "nama_lengkap": "TomoChain(Viction)", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Vietnam adoption, TomoChain 2.0"},
    {"simbol": "ICX", "nama_lengkap": "ICON", "kategori": "Interoperability", "volume_perdagangan": "Rendah", "potensi_katalis": "Interoperability, Korean blockchain"},
    {"simbol": "MAV", "nama_lengkap": "Maverick Protocol", "kategori": "DeFi / DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "Concentrated liquidity, Maverick 2.0"},
    {"simbol": "ARKM", "nama_lengkap": "Arkham", "kategori": "Blockchain Intelligence", "volume_perdagangan": "Rendah", "potensi_katalis": "On-chain analytics demand, compliance tools"},
    {"simbol": "ARK", "nama_lengkap": "Ark", "kategori": "Lapis 1 / Platform", "volume_perdagangan": "Rendah", "potensi_katalis": "SmartBridge tech, ARK DPoS"},
    {"simbol": "LOOM", "nama_lengkap": "Loom Network", "kategori": "Lapis 2 / Gaming", "volume_perdagangan": "Rendah", "potensi_katalis": "Gaming dApps, Polygon integration"},
    {"simbol": "MDX", "nama_lengkap": "Mdex", "kategori": "DeFi / DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "BSC+HECO DEX, mining rewards"},
    {"simbol": "STEEM", "nama_lengkap": "Steem", "kategori": "Social Media", "volume_perdagangan": "Rendah", "potensi_katalis": "Social media rewards, Steemit"},
    {"simbol": "CTSI", "nama_lengkap": "Cartesi", "kategori": "Lapis 2 / Optimistic Rollups", "volume_perdagangan": "Rendah", "potensi_katalis": "Linux on blockchain, dApp scaling"},
    {"simbol": "ONG", "nama_lengkap": "Ontology Gas", "kategori": "Gas Token", "volume_perdagangan": "Rendah", "potensi_katalis": "Ontology ecosystem, ONG utility"},
    {"simbol": "COS", "nama_lengkap": "Contentos", "kategori": "Content", "volume_perdagangan": "Rendah", "potensi_katalis": "Video content platform, creator economy"},
    {"simbol": "DEFI", "nama_lengkap": "De.Fi", "kategori": "DeFi / Security", "volume_perdagangan": "Rendah", "potensi_katalis": "DeFi security tools, anti-phishing"},
    {"simbol": "XTZ", "nama_lengkap": "Tezos", "kategori": "Lapis 1 / Smart Contracts", "volume_perdagangan": "Sedang", "potensi_katalis": "Baking rewards, formal verification"},
    {"simbol": "QI", "nama_lengkap": "BENQI", "kategori": "DeFi / Lending (Avalanche)", "volume_perdagangan": "Rendah", "potensi_katalis": "Avalanche lending, QI tokenomics"},
    {"simbol": "BTS", "nama_lengkap": "BitShares", "kategori": "DEX / Platform", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized exchange, BitAssets"},
    {"simbol": "PHB", "nama_lengkap": "Phoenix AI", "kategori": "Infrastructure / AI", "volume_perdagangan": "Rendah", "potensi_katalis": "AI infrastructure, Phoenix Global"},
    {"simbol": "GLMR", "nama_lengkap": "Moonbeam", "kategori": "Parachain / EVM (Polkadot)", "volume_perdagangan": "Sedang", "potensi_katalis": "EVM compatibility, Polkadot parachain"},
    {"simbol": "RAY", "nama_lengkap": "Raydium", "kategori": "DeFi / DEX (Solana)", "volume_perdagangan": "Sedang", "potensi_katalis": "Solana AMM, Serum integration"},
    {"simbol": "FOOTBALL", "nama_lengkap": "Fan Token Index", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "Football fan tokens, sports events"},
    {"simbol": "BLUEBIRD", "nama_lengkap": "Bluebird Index", "kategori": "Social Index", "volume_perdagangan": "Rendah", "potensi_katalis": "Social media trends, blue bird index"},
    {"simbol": "POLYX", "nama_lengkap": "Polymesh", "kategori": "RWA / Security Tokens", "volume_perdagangan": "Rendah", "potensi_katalis": "Security token issuance, Polymath rebrand"},
    {"simbol": "TOKEN", "nama_lengkap": "TokenFi", "kategori": "Tokenization", "volume_perdagangan": "Rendah", "potensi_katalis": "Token launchpad, token services"},
    {"simbol": "KDA", "nama_lengkap": "Kadena", "kategori": "Lapis 1 / PoW", "volume_perdagangan": "Sedang", "potensi_katalis": "Scalable PoW, Pact smart contracts"},
    {"simbol": "SLP", "nama_lengkap": "Smooth Love Potion", "kategori": "Gaming / Axie Infinity", "volume_perdagangan": "Rendah", "potensi_katalis": "Axie Infinity breeding, scholarship"},
    {"simbol": "SPELL", "nama_lengkap": "Spell Token", "kategori": "DeFi / Lending", "volume_perdagangan": "Rendah", "potensi_katalis": "Abracadabra.money, SPELL staking"},
    {"simbol": "ALICE", "nama_lengkap": "MyNeighborAlice", "kategori": "Gaming / Metaverse", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT game updates, virtual islands"},
    {"simbol": "BURGER", "nama_lengkap": "BurgerCities", "kategori": "DeFi / Metaverse", "volume_perdagangan": "Rendah", "potensi_katalis": "BurgerSwap, metaverse cities"},
    {"simbol": "PYR", "nama_lengkap": "Vulcan Forged", "kategori": "Gaming", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT game launches, PYR burning"},
    {"simbol": "GHST", "nama_lengkap": "Aavegotchi", "kategori": "DeFi / NFT Gaming", "volume_perdagangan": "Rendah", "potensi_katalis": "Aavegotchi NFTs, GHST staking"},
    {"simbol": "TLM", "nama_lengkap": "Alien Worlds", "kategori": "Gaming / Metaverse", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT drops, Trilium mining"},
    {"simbol": "DAR", "nama_lengkap": "Mines of Dalarnia", "kategori": "Gaming", "volume_perdagangan": "Rendah", "potensi_katalis": "Play-to-earn mining, DAR tokenomics"},
    {"simbol": "VOXEL", "nama_lengkap": "Voxies", "kategori": "Gaming", "volume_perdagangan": "Rendah", "potensi_katalis": "Voxel-based RPG, NFT characters"},
    {"simbol": "AXL", "nama_lengkap": "Axelar", "kategori": "Interoperability", "volume_perdagangan": "Sedang", "potensi_katalis": "Cross-chain dApp adoption, validator growth"},
    {"simbol": "GLM", "nama_lengkap": "Golem", "kategori": "DePIN / Computation", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized computing, Blender rendering"},
    {"simbol": "FIS", "nama_lengkap": "StaFi", "kategori": "Liquid Staking", "volume_perdagangan": "Rendah", "potensi_katalis": "Staked token liquidity, rToken issuance"},
    {"simbol": "OAX", "nama_lengkap": "OAX", "kategori": "DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "OpenANX, decentralized exchange"},
    {"simbol": "WAN", "nama_lengkap": "Wanchain", "kategori": "Interoperability", "volume_perdagangan": "Rendah", "potensi_katalis": "Cross-chain bridges, WAN staking"},
    {"simbol": "HIFI", "nama_lengkap": "Hifi Finance", "kategori": "DeFi / Lending", "volume_perdagangan": "Rendah", "potensi_katalis": "Fixed-rate lending, HIFI governance"},
    {"simbol": "PROS", "nama_lengkap": "Prosper", "kategori": "Prediction Market", "volume_perdagangan": "Rendah", "potensi_katalis": "Crypto prediction markets, PROS token"},
    {"simbol": "VITE", "nama_lengkap": "Vite", "kategori": "DAG / Platform", "volume_perdagangan": "Rendah", "potensi_katalis": "High-frequency transactions, ViteX DEX"},
    {"simbol": "FOR", "nama_lengkap": "ForTube", "kategori": "DeFi / Lending", "volume_perdagangan": "Rendah", "potensi_katalis": "DeFi lending, FOR tokenomics"},
    {"simbol": "PNT", "nama_lengkap": "pNetwork", "kategori": "Interoperability", "volume_perdagangan": "Rendah", "potensi_katalis": "Cross-chain asset wrapping, pToken issuance"},
    {"simbol": "MBOX", "nama_lengkap": "MOBOX", "kategori": "GameFi", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT farming, yield farming"},
    {"simbol": "LAZIO", "nama_lengkap": "S.S. Lazio Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "S.S. Lazio matches, fan engagement"},
    {"simbol": "PORTO", "nama_lengkap": "FC Porto Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "FC Porto matches, fan engagement"},
    {"simbol": "SANTOS", "nama_lengkap": "Santos FC Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "Santos FC matches, fan engagement"},
    {"simbol": "PSG", "nama_lengkap": "Paris Saint-Germain Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "PSG matches, fan engagement"},
    {"simbol": "JUV", "nama_lengkap": "Juventus Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "Juventus matches, fan engagement"},
    {"simbol": "CITY", "nama_lengkap": "Manchester City Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "Manchester City matches, fan engagement"},
    {"simbol": "BAR", "nama_lengkap": "FC Barcelona Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "FC Barcelona matches, fan engagement"},
    {"simbol": "ACM", "nama_lengkap": "AC Milan Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "AC Milan matches, fan engagement"},
    {"simbol": "ATM", "nama_lengkap": "Atletico de Madrid Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "Atletico matches, fan engagement"},
    {"simbol": "ASR", "nama_lengkap": "AS Roma Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "AS Roma matches, fan engagement"},
    {"simbol": "OG", "nama_lengkap": "OG Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "OG esports, fan engagement"},
    {"simbol": "ALPINE", "nama_lengkap": "Alpine F1 Team Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "F1 races, Alpine team"},
    {"simbol": "WING", "nama_lengkap": "Wing Finance", "kategori": "DeFi / Lending", "volume_perdagangan": "Rendah", "potensi_katalis": "DeFi lending, WING tokenomics"},
    {"simbol": "FIRO", "nama_lengkap": "Firo", "kategori": "Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "Zerocoin protocol, privacy tech"},
    {"simbol": "TFUEL", "nama_lengkap": "Theta Fuel", "kategori": "Gas Token", "volume_perdagangan": "Rendah", "potensi_katalis": "Theta video streaming, TFUEL utility"},
    {"simbol": "AKRO", "nama_lengkap": "Akropolis", "kategori": "DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "DeFi yield, AKRO governance"},
    {"simbol": "UTK", "nama_lengkap": "xMoney", "kategori": "Payments", "volume_perdagangan": "Rendah", "potensi_katalis": "Cross-border payments, UTK utility"},
    {"simbol": "SFP", "nama_lengkap": "SafePal", "kategori": "Hardware Wallet", "volume_perdagangan": "Rendah", "potensi_katalis": "Hardware wallet adoption, SFP tokenomics"},
    # --- Dari CSV table-5fa3893f-a31b-4961-a60e-b81b5bbf0ee7-8.csv ---
    {"simbol": "XLM", "nama_lengkap": "Stellar", "kategori": "Payment", "volume_perdagangan": "Tinggi", "potensi_katalis": "Remittance partnerships (MoneyGram)"},
    {"simbol": "THETA", "nama_lengkap": "Theta Network", "kategori": "Video", "volume_perdagangan": "Tinggi", "potensi_katalis": "Partnerships (Sony, Samsung)"},
    {"simbol": "ALGO", "nama_lengkap": "Algorand", "kategori": "Lapis 1", "volume_perdagangan": "Sedang-Tinggi", "potensi_katalis": "Governance rewards"},
    {"simbol": "ETC", "nama_lengkap": "Ethereum Classic", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "51% attack fears"},
    {"simbol": "XMR", "nama_lengkap": "Monero", "kategori": "Privacy", "volume_perdagangan": "Sedang", "potensi_katalis": "Privacy coin regulation"},
    {"simbol": "CAKE", "nama_lengkap": "PancakeSwap", "kategori": "DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "IFO launches"},
    {"simbol": "VET", "nama_lengkap": "VeChain", "kategori": "Supply Chain", "volume_perdagangan": "Sedang", "potensi_katalis": "Corporate partnerships (Walmart China)"},
    {"simbol": "EOS", "nama_lengkap": "EOS", "kategori": "Lapis 1", "volume_perdagangan": "Rendah-Sedang", "potensi_katalis": "Block producer elections"},
    {"simbol": "KSM", "nama_lengkap": "Kusama", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Polkadot parachain auctions"},
    {"simbol": "XTZ", "nama_lengkap": "Tezos", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Baking rewards announcements"},
    {"simbol": "NEO", "nama_lengkap": "NEO", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "China regulation"},
    {"simbol": "DASH", "nama_lengkap": "Dash", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Adoption in hyperinflationary countries (Venezuela)"},
    {"simbol": "ZEC", "nama_lengkap": "Zcash", "kategori": "Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "Halving events"},
    {"simbol": "MKR", "nama_lengkap": "Maker", "kategori": "DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "DAI stability fees"},
    {"simbol": "COMP", "nama_lengkap": "Compound", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Governance proposals"},
    {"simbol": "YFI", "nama_lengkap": "Yearn.Finance", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Andre Cronje tweets"},
    {"simbol": "SNX", "nama_lengkap": "Synthetix", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Synthetic asset demand"},
    {"simbol": "AAVE", "nama_lengkap": "Aave", "kategori": "DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "Liquidity mining launches"},
    {"simbol": "SUSHI", "nama_lengkap": "SushiSwap", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Onsen menu additions"},
    {"simbol": "CRV", "nama_lengkap": "Curve", "kategori": "DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "Pool gauge wars"},
    {"simbol": "RUNE", "nama_lengkap": "THORChain", "kategori": "Cross-Chain", "volume_perdagangan": "Tinggi", "potensi_katalis": "Liquidity depth increase in major assets"},
    {"simbol": "LDO", "nama_lengkap": "Lido", "kategori": "Staking", "volume_perdagangan": "Tinggi", "potensi_katalis": "stETH depegging fears"},
    {"simbol": "GMX", "nama_lengkap": "GMX", "kategori": "Perp DEX", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "BTC/ETH volatility (>5% daily move)"},
    {"simbol": "DYDX", "nama_lengkap": "dYdX", "kategori": "Perp DEX", "volume_perdagangan": "Tinggi", "potensi_katalis": "Trading competitions"},
    {"simbol": "OP", "nama_lengkap": "Optimism", "kategori": "Lapis 2", "volume_perdagangan": "Tinggi", "potensi_katalis": "OP token airdrops"},
    {"simbol": "ARB", "nama_lengkap": "Arbitrum", "kategori": "Lapis 2", "volume_perdagangan": "Tinggi", "potensi_katalis": "Arbitrum Odyssey"},
    {"simbol": "LUNA", "nama_lengkap": "Terra (v2)", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Community proposals (UST peg recovery)"},
    {"simbol": "FTT", "nama_lengkap": "FTX Token", "kategori": "Exchange", "volume_perdagangan": "Rendah", "potensi_katalis": "FTX-related news only"},
    {"simbol": "RAY", "nama_lengkap": "Raydium", "kategori": "DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "Solana NFT launches"},
    {"simbol": "HBAR", "nama_lengkap": "Hedera", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": "Governance council news (Google, IBM)"},
    {"simbol": "ICP", "nama_lengkap": "Internet Computer", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Canister smart contract updates"},
    # --- Dari CSV table-5fa3893f-a31b-4961-a60e-b81b5bbf0ee7-11.csv ---
    {"simbol": "AXS", "nama_lengkap": "Axie Infinity", "kategori": "Gaming", "volume_perdagangan": "Tinggi", "potensi_katalis": "Scholarship demand & token unlocks"},
    {"simbol": "SAND", "nama_lengkap": "The Sandbox", "kategori": "Metaverse", "volume_perdagangan": "Tinggi", "potensi_katalis": "Celebrity partnerships (Snoop Dogg)"},
    {"simbol": "MANA", "nama_lengkap": "Decentraland", "kategori": "Metaverse", "volume_perdagangan": "Sedang", "potensi_katalis": "Virtual land sales"},
    {"simbol": "ENJ", "nama_lengkap": "Enjin Coin", "kategori": "Gaming", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT collaborations (Minecraft)"},
    {"simbol": "CHZ", "nama_lengkap": "Chiliz", "kategori": "Fan Token", "volume_perdagangan": "Sedang", "potensi_katalis": "Sports events (Champions League)"},
    {"simbol": "GALA", "nama_lengkap": "Gala Games", "kategori": "Gaming", "volume_perdagangan": "Tinggi", "potensi_katalis": "Game launches (Town Star)"},
    {"simbol": "FLOW", "nama_lengkap": "Flow", "kategori": "NFT", "volume_perdagangan": "Sedang", "potensi_katalis": "NBA Top Shot activity"},
    {"simbol": "CRO", "nama_lengkap": "Crypto.com Coin", "kategori": "Exchange", "volume_perdagangan": "Sedang", "potensi_katalis": "CRO staking rewards announcements"},
    {"simbol": "KLAY", "nama_lengkap": "Klaytn", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Adoption in South Korea"},
    {"simbol": "ROSE", "nama_lengkap": "Oasis Network", "kategori": "Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "DeFi privacy demand"},
    {"simbol": "CELO", "nama_lengkap": "Celo", "kategori": "Payment", "volume_perdagangan": "Sedang", "potensi_katalis": "Mobile payment adoption in developing countries"},
    {"simbol": "EGLD", "nama_lengkap": "MultiversX (ex-Elrond)", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Web3 mobile adoption"},
    {"simbol": "ICX", "nama_lengkap": "ICON", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Partnerships in Korea"},
    {"simbol": "ZIL", "nama_lengkap": "Zilliqa", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT marketplace activity"},
    {"simbol": "TOMO", "nama_lengkap": "TomoChain", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Adoption in Southeast Asia"},
    {"simbol": "ONE", "nama_lengkap": "Harmony", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Bridge security incidents"},
    {"simbol": "NULS", "nama_lengkap": "NULS", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Cross-chain demand"},
    {"simbol": "WAX", "nama_lengkap": "WAXP", "kategori": "NFT", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT drops (Alien Worlds)"},
    {"simbol": "QTUM", "nama_lengkap": "Qtum", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Smart contract updates"},
    {"simbol": "STX", "nama_lengkap": "Stacks", "kategori": "Bitcoin Layer", "volume_perdagangan": "Sedang", "potensi_katalis": "Bitcoin NFT activity"},
    {"simbol": "LSK", "nama_lengkap": "Lisk", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "JavaScript SDK updates"},
    {"simbol": "RVN", "nama_lengkap": "Ravencoin", "kategori": "Asset Tokenization", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT/meme coin launches"},
    {"simbol": "SC", "nama_lengkap": "Siacoin", "kategori": "Storage", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized storage demand"},
    {"simbol": "XEM", "nama_lengkap": "NEM", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Partnerships in Japan"},
    {"simbol": "DCR", "nama_lengkap": "Decred", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Governance voting"},
    {"simbol": "ZEN", "nama_lengkap": "Horizen", "kategori": "Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "Node operator demand"},
    {"simbol": "KAVA", "nama_lengkap": "Kava", "kategori": "Cross-Chain", "volume_perdagangan": "Sedang", "potensi_katalis": "Multi-chain DeFi integrations"},
    {"simbol": "IRIS", "nama_lengkap": "IRISnet", "kategori": "Cross-Chain", "volume_perdagangan": "Rendah", "potensi_katalis": "Cosmos ecosystem growth"},
    {"simbol": "LPT", "nama_lengkap": "Livepeer", "kategori": "Video Streaming", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized video demand"},
    {"simbol": "DGB", "nama_lengkap": "DigiByte", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Merchant adoption"},
    {"simbol": "NANO", "nama_lengkap": "Nano", "kategori": "Payment", "volume_perdagangan": "Sedang", "potensi_katalis": "Zero-fee transaction demand"},
    {"simbol": "XDC", "nama_lengkap": "XinFin", "kategori": "Enterprise", "volume_perdagangan": "Rendah", "potensi_katalis": "Supply chain partnerships"},
    {"simbol": "HNT", "nama_lengkap": "Helium", "kategori": "IoT", "volume_perdagangan": "Sedang", "potensi_katalis": "5G hotspot deployments"},
    {"simbol": "BTT", "nama_lengkap": "BitTorrent", "kategori": "Storage", "volume_perdagangan": "Sedang", "potensi_katalis": "BitTorrent user growth"},
    {"simbol": "NEXO", "nama_lengkap": "Nexo", "kategori": "Lending", "volume_perdagangan": "Sedang", "potensi_katalis": "Staking rewards"},
    {"simbol": "CEL", "nama_lengkap": "Celo", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Mobile wallet adoption"},
    {"simbol": "REN", "nama_lengkap": "Ren", "kategori": "Cross-Chain", "volume_perdagangan": "Rendah", "potensi_katalis": "Bridge usage"},
    {"simbol": "OMG", "nama_lengkap": "OMG Network", "kategori": "Lapis 2", "volume_perdagangan": "Rendah", "potensi_katalis": "Ethereum scaling demand"},
    {"simbol": "SXP", "nama_lengkap": "Swipe", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Crypto card adoption"},
    {"simbol": "BAKE", "nama_lengkap": "BakerySwap", "kategori": "DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "Binance Smart Chain activity"},
    {"simbol": "AUDIO", "nama_lengkap": "Audius", "kategori": "Music", "volume_perdagangan": "Sedang", "potensi_katalis": "Artist migrations"},
    {"simbol": "CTK", "nama_lengkap": "CoTrader", "kategori": "Social Trading", "volume_perdagangan": "Rendah", "potensi_katalis": "Copy trading demand"},
    {"simbol": "DFI", "nama_lengkap": "DeFiChain", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Bitcoin DeFi activity"},
    {"simbol": "FIO", "nama_lengkap": "FIO Protocol", "kategori": "UX", "volume_perdagangan": "Rendah", "potensi_katalis": "Wallet integration announcements"},
    {"simbol": "JST", "nama_lengkap": "Just", "kategori": "DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "TRON ecosystem growth"},
    {"simbol": "LINA", "nama_lengkap": "Linear", "kategori": "DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "Cross-chain DeFi"},
    {"simbol": "LRC", "nama_lengkap": "Loopring", "kategori": "Lapis 2", "volume_perdagangan": "Sedang", "potensi_katalis": "ZK-Rollup adoption"},
    {"simbol": "MIR", "nama_lengkap": "Mirror Protocol", "kategori": "Synthetic Assets", "volume_perdagangan": "Rendah", "potensi_katalis": "Terra ecosystem news"},
    {"simbol": "OGN", "nama_lengkap": "Origin Protocol", "kategori": "NFT", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT marketplace activity"},
    {"simbol": "OMI", "nama_lengkap": "Omega", "kategori": "Metaverse", "volume_perdagangan": "Rendah", "potensi_katalis": "Star Atlas updates"},
    {"simbol": "PERP", "nama_lengkap": "Perpetual Protocol", "kategori": "Perp DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "BTC/ETH volatility"},
    {"simbol": "POND", "nama_lengkap": "Marlin", "kategori": "Infrastructure", "volume_perdagangan": "Rendah", "potensi_katalis": "Mempool optimization demand"},
    {"simbol": "PYR", "nama_lengkap": "Vulcan Forged", "kategori": "Gaming", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT game launches"},
    {"simbol": "RGT", "nama_lengkap": "Radiant Capital", "kategori": "Lending", "volume_perdagangan": "Rendah", "potensi_katalis": "Interest rate changes"},
    {"simbol": "SKL", "nama_lengkap": "SKALE", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Ethereum scaling demand"},
    {"simbol": "SSV", "nama_lengkap": "SSV Network", "kategori": "Staking", "volume_perdagangan": "Sedang", "potensi_katalis": "Ethereum staking growth"},
    {"simbol": "SUN", "nama_lengkap": "Sun", "kategori": "TRON Ecosystem", "volume_perdagangan": "Rendah", "potensi_katalis": "TRON DeFi activity"},
    {"simbol": "TLM", "nama_lengkap": "Alien Worlds", "kategori": "Gaming", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT drops"},
    {"simbol": "UMA", "nama_lengkap": "UMA", "kategori": "Oracle", "volume_perdagangan": "Rendah", "potensi_katalis": "Optimistic oracle usage"},
    {"simbol": "UOS", "nama_lengkap": "Ultra", "kategori": "Gaming", "volume_perdagangan": "Rendah", "potensi_katalis": "Gaming platform adoption"},
    {"simbol": "VIDT", "nama_lengkap": "VIDT Dacxi", "kategori": "NFT", "volume_perdagangan": "Rendah", "potensi_katalis": "Document verification demand"},
    {"simbol": "WOO", "nama_lengkap": "WOO Network", "kategori": "Liquidity", "volume_perdagangan": "Tinggi", "potensi_katalis": "Institutional inflow"},
    {"simbol": "XVS", "nama_lengkap": "Venus", "kategori": "Lending", "volume_perdagangan": "Sedang", "potensi_katalis": "Binance Smart Chain activity"},
    {"simbol": "YFII", "nama_lengkap": "YFII", "kategori": "DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "Governance proposals"},
    {"simbol": "ZRX", "nama_lengkap": "0x", "kategori": "DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT marketplace activity"},
    {"simbol": "AERGO", "nama_lengkap": "Aergo", "kategori": "Enterprise", "volume_perdagangan": "Rendah", "potensi_katalis": "Partnerships in Korea"},
    {"simbol": "ALICE", "nama_lengkap": "My Neighbor Alice", "kategori": "Metaverse", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT game updates"},
    {"simbol": "ASR", "nama_lengkap": "AS Roma Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "Football matches"},
    {"simbol": "ATLAS", "nama_lengkap": "Star Atlas", "kategori": "Gaming", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT marketplace activity"},
    {"simbol": "AUCTION", "nama_lengkap": "BakerySwap", "kategori": "DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "BSC ecosystem growth"},
    {"simbol": "BADGER", "nama_lengkap": "BadgerDAO", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "BTC DeFi activity"},
    {"simbol": "BAL", "nama_lengkap": "Balancer", "kategori": "DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "veBAL emissions"},
    {"simbol": "BAND", "nama_lengkap": "Band Protocol", "kategori": "Oracle", "volume_perdagangan": "Sedang", "potensi_katalis": "Cross-chain data demand"},
    {"simbol": "BICO", "nama_lengkap": "Blockchain.com Token", "kategori": "Exchange", "volume_perdagangan": "Rendah", "potensi_katalis": "Exchange listing news"},
    {"simbol": "BNT", "nama_lengkap": "Bancor", "kategori": "DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "Impermanent loss protection"},
    {"simbol": "C98", "nama_lengkap": "Coin98", "kategori": "Wallet", "volume_perdagangan": "Sedang", "potensi_katalis": "Wallet adoption"},
    {"simbol": "CKB", "nama_lengkap": "Nervos Network", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Bitcoin layer 2 demand"},
    {"simbol": "CEEK", "nama_lengkap": "CEEK VR", "kategori": "Metaverse", "volume_perdagangan": "Rendah", "potensi_katalis": "VR concert demand"},
    {"simbol": "COTI", "nama_lengkap": "COTI", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "DAG technology news"},
    {"simbol": "CVC", "nama_lengkap": "Civic", "kategori": "Identity", "volume_perdagangan": "Rendah", "potensi_katalis": "KYC/AML regulation news"},
    {"simbol": "DENT", "nama_lengkap": "Dent", "kategori": "Telecom", "volume_perdagangan": "Rendah", "potensi_katalis": "Mobile data marketplace"},
    {"simbol": "DGB", "nama_lengkap": "DigiByte", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Merchant adoption"},
    {"simbol": "DIA", "nama_lengkap": "DIA", "kategori": "Oracle", "volume_perdagangan": "Rendah", "potensi_katalis": "Data marketplace demand"},
    {"simbol": "DNT", "nama_lengkap": "district0x", "kategori": "Marketplace", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT marketplace activity"},
    {"simbol": "EGLD", "nama_lengkap": "Elrond", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "MultiversX rebrand"},
    {"simbol": "ELF", "nama_lengkap": "aelf", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Enterprise blockchain demand"},
    {"simbol": "ERG", "nama_lengkap": "Ergo", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Proof-of-work innovation"},
    {"simbol": "ESS", "nama_lengkap": "ESS", "kategori": "Identity", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized identity demand"},
    {"simbol": "FET", "nama_lengkap": "Fetch.ai", "kategori": "AI", "volume_perdagangan": "Sedang", "potensi_katalis": "AI + blockchain news"},
    {"simbol": "FUN", "nama_lengkap": "FunFair", "kategori": "Gaming", "volume_perdagangan": "Rendah", "potensi_katalis": "iGaming regulation news"},
    {"simbol": "GRT", "nama_lengkap": "The Graph", "kategori": "Indexing", "volume_perdagangan": "Tinggi", "potensi_katalis": "Query demand"},
    {"simbol": "GTC", "nama_lengkap": "Gitcoin", "kategori": "Funding", "volume_perdagangan": "Sedang", "potensi_katalis": "Grants rounds"},
    {"simbol": "HBAR", "nama_lengkap": "Hedera Hashgraph", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": "Governance council news"},
    {"simbol": "HFT", "nama_lengkap": "Hashflow", "kategori": "DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "MEV protection demand"},
    {"simbol": "HOT", "nama_lengkap": "Hydro Protocol", "kategori": "Identity", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized identity news"},
    {"simbol": "ICX", "nama_lengkap": "ICON", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Korea blockchain adoption"},
    {"simbol": "ILV", "nama_lengkap": "Illuvium", "kategori": "Gaming", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT drops"},
    {"simbol": "INJ", "nama_lengkap": "Injective Protocol", "kategori": "DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "Derivatives trading demand"},
    {"simbol": "JASMY", "nama_lengkap": "Jasmy", "kategori": "IoT", "volume_perdagangan": "Sedang", "potensi_katalis": "Japan IoT adoption"},
    {"simbol": "JST", "nama_lengkap": "Just", "kategori": "DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "TRON ecosystem growth"},
    # --- Dari CSV table-5fa3893f-a31b-4961-a60e-b81b5bbf0ee7-16.csv ---
    {"simbol": "ACH", "nama_lengkap": "Achieve", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Listing di exchange besar"},
    {"simbol": "AGIX", "nama_lengkap": "SingularityNET", "kategori": "AI", "volume_perdagangan": "Sedang", "potensi_katalis": "Kolaborasi dengan proyek AI besar"},
    {"simbol": "ALPACA", "nama_lengkap": "Alpaca Finance", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Leverage yield farming"},
    {"simbol": "API3", "nama_lengkap": "API3", "kategori": "Oracle", "volume_perdagangan": "Sedang", "potensi_katalis": "dAPI adoption oleh proyek DeFi"},
    {"simbol": "ARDR", "nama_lengkap": "Ardor", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Child chain launches"},
    {"simbol": "ARPA", "nama_lengkap": "ARPA Chain", "kategori": "Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "MPC protocol updates"},
    {"simbol": "ASR", "nama_lengkap": "AS Roma Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "Pertandingan sepakbola"},
    {"simbol": "AUDIO", "nama_lengkap": "Audius", "kategori": "Music", "volume_perdagangan": "Sedang", "potensi_katalis": "Artist migrations"},
    {"simbol": "AVAX", "nama_lengkap": "Avalanche", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": "Subnet launches"},
    {"simbol": "BADGER", "nama_lengkap": "BadgerDAO", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "WBTC vaults"},
    {"simbol": "BAL", "nama_lengkap": "Balancer", "kategori": "DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "veBAL emissions"},
    {"simbol": "BAND", "nama_lengkap": "Band Protocol", "kategori": "Oracle", "volume_perdagangan": "Sedang", "potensi_katalis": "Cross-chain data demand"},
    {"simbol": "BICO", "nama_lengkap": "Blockchain.com Token", "kategori": "Exchange", "volume_perdagangan": "Rendah", "potensi_katalis": "Listing exchange baru"},
    {"simbol": "BNT", "nama_lengkap": "Bancor", "kategori": "DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "Impermanent loss protection"},
    {"simbol": "C98", "nama_lengkap": "Coin98", "kategori": "Wallet", "volume_perdagangan": "Sedang", "potensi_katalis": "Wallet adoption"},
    {"simbol": "CKB", "nama_lengkap": "Nervos Network", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Bitcoin layer 2 demand"},
    {"simbol": "CEEK", "nama_lengkap": "CEEK VR", "kategori": "Metaverse", "volume_perdagangan": "Rendah", "potensi_katalis": "VR concerts"},
    {"simbol": "COTI", "nama_lengkap": "COTI", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "DAG technology news"},
    {"simbol": "CVC", "nama_lengkap": "Civic", "kategori": "Identity", "volume_perdagangan": "Rendah", "potensi_katalis": "KYC/AML regulation news"},
    {"simbol": "DENT", "nama_lengkap": "Dent", "kategori": "Telecom", "volume_perdagangan": "Rendah", "potensi_katalis": "Mobile data marketplace"},
    {"simbol": "DGB", "nama_lengkap": "DigiByte", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Merchant adoption"},
    {"simbol": "DIA", "nama_lengkap": "DIA", "kategori": "Oracle", "volume_perdagangan": "Rendah", "potensi_katalis": "Data marketplace demand"},
    {"simbol": "DNT", "nama_lengkap": "district0x", "kategori": "Marketplace", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT marketplace activity"},
    {"simbol": "EGLD", "nama_lengkap": "Elrond", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "MultiversX rebrand"},
    {"simbol": "ELF", "nama_lengkap": "aelf", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Enterprise blockchain demand"},
    {"simbol": "ERG", "nama_lengkap": "Ergo", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Proof-of-work innovation"},
    {"simbol": "ESS", "nama_lengkap": "ESS", "kategori": "Identity", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized identity demand"},
    {"simbol": "FET", "nama_lengkap": "Fetch.ai", "kategori": "AI", "volume_perdagangan": "Sedang", "potensi_katalis": "AI + blockchain news"},
    {"simbol": "FUN", "nama_lengkap": "FunFair", "kategori": "Gaming", "volume_perdagangan": "Rendah", "potensi_katalis": "iGaming regulation news"},
    {"simbol": "GRT", "nama_lengkap": "The Graph", "kategori": "Indexing", "volume_perdagangan": "Tinggi", "potensi_katalis": "Query demand"},
    {"simbol": "GTC", "nama_lengkap": "Gitcoin", "kategori": "Funding", "volume_perdagangan": "Sedang", "potensi_katalis": "Grants rounds"},
    {"simbol": "HBAR", "nama_lengkap": "Hedera", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": "Governance council news"},
    {"simbol": "HFT", "nama_lengkap": "Hashflow", "kategori": "DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "MEV protection demand"},
    {"simbol": "HOT", "nama_lengkap": "Hydro Protocol", "kategori": "Identity", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized identity news"},
    {"simbol": "ICX", "nama_lengkap": "ICON", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Korea blockchain adoption"},
    {"simbol": "ILV", "nama_lengkap": "Illuvium", "kategori": "Gaming", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT drops"},
    {"simbol": "INJ", "nama_lengkap": "Injective Protocol", "kategori": "DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "Derivatives trading demand"},
    {"simbol": "JASMY", "nama_lengkap": "Jasmy", "kategori": "IoT", "volume_perdagangan": "Sedang", "potensi_katalis": "Japan IoT adoption"},
    {"simbol": "JST", "nama_lengkap": "Just", "kategori": "DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "TRON ecosystem growth"},
    {"simbol": "KDA", "nama_lengkap": "Kadena", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Scalability claims"},
    {"simbol": "KIN", "nama_lengkap": "Kin", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Social app integrations"},
    {"simbol": "KLAY", "nama_lengkap": "Klaytn", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Korea adoption"},
    {"simbol": "KSM", "nama_lengkap": "Kusama", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Polkadot parachain auctions"},
    {"simbol": "LINA", "nama_lengkap": "Linear", "kategori": "DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "Cross-chain DeFi"},
    {"simbol": "LRC", "nama_lengkap": "Loopring", "kategori": "Lapis 2", "volume_perdagangan": "Sedang", "potensi_katalis": "ZK-Rollup adoption"},
    {"simbol": "MIR", "nama_lengkap": "Mirror Protocol", "kategori": "Synthetic Assets", "volume_perdagangan": "Rendah", "potensi_katalis": "Terra ecosystem news"},
    {"simbol": "NKN", "nama_lengkap": "NKN", "kategori": "Infrastructure", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized network demand"},
    {"simbol": "NMR", "nama_lengkap": "Numerai", "kategori": "AI", "volume_perdagangan": "Rendah", "potensi_katalis": "AI tournament results"},
    {"simbol": "OCEAN", "nama_lengkap": "Ocean Protocol", "kategori": "Data", "volume_perdagangan": "Rendah", "potensi_katalis": "Data marketplace activity"},
    {"simbol": "OGN", "nama_lengkap": "Origin Protocol", "kategori": "NFT", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT marketplace activity"},
    {"simbol": "OMI", "nama_lengkap": "Omega", "kategori": "Metaverse", "volume_perdagangan": "Rendah", "potensi_katalis": "Star Atlas updates"},
    {"simbol": "ONT", "nama_lengkap": "Ontology", "kategori": "Identity", "volume_perdagangan": "Rendah", "potensi_katalis": "Enterprise identity solutions"},
    {"simbol": "OXT", "nama_lengkap": "Orchid", "kategori": "Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "VPN demand"},
    {"simbol": "PHB", "nama_lengkap": "Phoenix Global", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Enterprise blockchain demand"},
    {"simbol": "POLY", "nama_lengkap": "Polygon", "kategori": "Lapis 2", "volume_perdagangan": "Tinggi", "potensi_katalis": "Ethereum gas wars"},
    {"simbol": "POWR", "nama_lengkap": "Power Ledger", "kategori": "Energy", "volume_perdagangan": "Rendah", "potensi_katalis": "Renewable energy trading"},
    {"simbol": "PUNDIX", "nama_lengkap": "Pundi X", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Crypto card adoption"},
    {"simbol": "QI", "nama_lengkap": "Qi Dao", "kategori": "Lending", "volume_perdagangan": "Sedang", "potensi_katalis": "MIM stablecoin demand"},
    {"simbol": "QNT", "nama_lengkap": "Quant", "kategori": "Interoperability", "volume_perdagangan": "Sedang", "potensi_katalis": "Enterprise blockchain adoption"},
    {"simbol": "QUICK", "nama_lengkap": "QuickSwap", "kategori": "DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "Polygon ecosystem growth"},
    {"simbol": "RARI", "nama_lengkap": "Rarible", "kategori": "NFT", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT marketplace activity"},
    {"simbol": "RDN", "nama_lengkap": "Raiden Network", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Off-chain scaling demand"},
    {"simbol": "RGT", "nama_lengkap": "Radiant Capital", "kategori": "Lending", "volume_perdagangan": "Rendah", "potensi_katalis": "Interest rate changes"},
    {"simbol": "ROSE", "nama_lengkap": "Oasis Network", "kategori": "Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "DeFi privacy demand"},
    {"simbol": "RSR", "nama_lengkap": "Reserve Rights", "kategori": "Stablecoin", "volume_perdagangan": "Rendah", "potensi_katalis": "RSV stablecoin adoption"},
    {"simbol": "SKL", "nama_lengkap": "SKALE", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Ethereum scaling demand"},
    {"simbol": "SSV", "nama_lengkap": "SSV Network", "kategori": "Staking", "volume_perdagangan": "Sedang", "potensi_katalis": "Ethereum staking growth"},
    {"simbol": "SUN", "nama_lengkap": "Sun", "kategori": "TRON Ecosystem", "volume_perdagangan": "Rendah", "potensi_katalis": "TRON DeFi activity"},
    {"simbol": "SUPER", "nama_lengkap": "SuperFarm", "kategori": "NFT", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT farming"},
    {"simbol": "SUSHI", "nama_lengkap": "SushiSwap", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Onsen menu additions"},
    {"simbol": "SXP", "nama_lengkap": "Swipe", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Crypto card adoption"},
    {"simbol": "TFUEL", "nama_lengkap": "Theta Fuel", "kategori": "Video", "volume_perdagangan": "Sedang", "potensi_katalis": "Theta EdgeStore demand"},
    {"simbol": "TLM", "nama_lengkap": "Alien Worlds", "kategori": "Gaming", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT drops"},
    {"simbol": "TRB", "nama_lengkap": "Tellor", "kategori": "Oracle", "volume_perdagangan": "Rendah", "potensi_katalis": "Decentralized oracle demand"},
    {"simbol": "TROY", "nama_lengkap": "TROY", "kategori": "Exchange", "volume_perdagangan": "Rendah", "potensi_katalis": "Exchange listing news"},
    {"simbol": "UMA", "nama_lengkap": "UMA", "kategori": "Oracle", "volume_perdagangan": "Rendah", "potensi_katalis": "Optimistic oracle usage"},
    {"simbol": "UOS", "nama_lengkap": "Ultra", "kategori": "Gaming", "volume_perdagangan": "Rendah", "potensi_katalis": "Gaming platform adoption"},
    {"simbol": "VIDT", "nama_lengkap": "VIDT Dacxi", "kategori": "NFT", "volume_perdagangan": "Rendah", "potensi_katalis": "Document verification demand"},
    {"simbol": "VOY", "nama_lengkap": "Voy", "kategori": "Exchange", "volume_perdagangan": "Rendah", "potensi_katalis": "Exchange listing news"},
    {"simbol": "WAXP", "nama_lengkap": "WAX", "kategori": "NFT", "volume_perdagangan": "Sedang", "potensi_katalis": "NFT marketplace activity"},
    {"simbol": "XNO", "nama_lengkap": "Nano", "kategori": "Payment", "volume_perdagangan": "Sedang", "potensi_katalis": "Zero-fee transaction demand"},
    {"simbol": "XTZ", "nama_lengkap": "Tezos", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Baking rewards"},
    {"simbol": "YFI", "nama_lengkap": "Yearn.Finance", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Andre Cronje tweets"},
    {"simbol": "YFII", "nama_lengkap": "YFII", "kategori": "DeFi", "volume_perdagangan": "Rendah", "potensi_katalis": "Governance proposals"},
    {"simbol": "ZIL", "nama_lengkap": "Zilliqa", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT marketplace activity"},
    {"simbol": "ZRX", "nama_lengkap": "0x", "kategori": "DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT marketplace activity"},
    {"simbol": "AERGO", "nama_lengkap": "Aergo", "kategori": "Enterprise", "volume_perdagangan": "Rendah", "potensi_katalis": "Korea enterprise adoption"},
    {"simbol": "ALICE", "nama_lengkap": "My Neighbor Alice", "kategori": "Metaverse", "volume_perdagangan": "Rendah", "potensi_katalis": "NFT game updates"},
    {"simbol": "ANT", "nama_lengkap": "Aragon", "kategori": "DAO", "volume_perdagangan": "Rendah", "potensi_katalis": "DAO tooling demand"},
    {"simbol": "API3", "nama_lengkap": "API3", "kategori": "Oracle", "volume_perdagangan": "Sedang", "potensi_katalis": "dAPI adoption"},
    {"simbol": "ARDR", "nama_lengkap": "Ardor", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Child chain launches"},
    {"simbol": "ARPA", "nama_lengkap": "ARPA Chain", "kategori": "Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "MPC protocol updates"},
    {"simbol": "ASR", "nama_lengkap": "AS Roma Fan Token", "kategori": "Fan Token", "volume_perdagangan": "Rendah", "potensi_katalis": "Football matches"},
    {"simbol": "AUDIO", "nama_lengkap": "Audius", "kategori": "Music", "volume_perdagangan": "Sedang", "potensi_katalis": "Artist migrations"},
    {"simbol": "AVAX", "nama_lengkap": "Avalanche", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": "Subnet launches"},
    {"simbol": "BADGER", "nama_lengkap": "BadgerDAO", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "WBTC vaults"},
    {"simbol": "BAL", "nama_lengkap": "Balancer", "kategori": "DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "veBAL emissions"},
    {"simbol": "BAND", "nama_lengkap": "Band Protocol", "kategori": "Oracle", "volume_perdagangan": "Sedang", "potensi_katalis": "Cross-chain data demand"},
    {"simbol": "BICO", "nama_lengkap": "Blockchain.com Token", "kategori": "Exchange", "volume_perdagangan": "Rendah", "potensi_katalis": "Exchange listing news"},
    {"simbol": "BNT", "nama_lengkap": "Bancor", "kategori": "DEX", "volume_perdagangan": "Rendah", "potensi_katalis": "Impermanent loss protection"},
    # --- Dari CSV table-5fa3893f-a31b-4961-a60e-b81b5bbf0ee7-19.csv ---
    {"simbol": "BTC", "nama_lengkap": "Bitcoin", "kategori": "Lapis 1", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Funding rate & liquidation clusters di $60K/$65K"},
    {"simbol": "ETH", "nama_lengkap": "Ethereum", "kategori": "Lapis 1", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Merge date (Sept 2022) as seasonal trend indicator"},
    {"simbol": "BNB", "nama_lengkap": "Binance Coin", "kategori": "Exchange", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Volume naik 40% saat Binance Burn Quarter (tiap Q1/Q3)"},
    {"simbol": "SOL", "nama_lengkap": "Solana", "kategori": "Lapis 1", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Volume dipengaruhi oleh NFT mints di Magic Eden"},
    {"simbol": "XRP", "nama_lengkap": "XRP", "kategori": "Payment", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Volume 3x lipat saat berita regulasi SEC"},
    {"simbol": "DOGE", "nama_lengkap": "Dogecoin", "kategori": "Meme", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Volume dipicu Elon Musk tweets (rata-rata +200% dalam 1 jam)"},
    {"simbol": "ADA", "nama_lengkap": "Cardano", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume naik saat hard fork (contoh: Vasil Upgrade 2022)"},
    {"simbol": "MATIC", "nama_lengkap": "Polygon", "kategori": "Lapis 2", "volume_perdagangan": "Tinggi", "potensi_katalis": 'Volume terkait dengan Ethereum gas wars" (saat gas >100 gwei, volume +35%"'},
    {"simbol": "DOT", "nama_lengkap": "Polkadot", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume dipengaruhi oleh * parachain auctions*"},
    {"simbol": "SHIB", "nama_lengkap": "Shiba Inu", "kategori": "Meme", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume dipicu oleh burn rate & kolaborasi metaverse"},
    {"simbol": "LTC", "nama_lengkap": "Litecoin", "kategori": "Payment", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume naik saat adopsi merchant meningkat"},
    {"simbol": "UNI", "nama_lengkap": "Uniswap", "kategori": "DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume terkait dengan governance votes & fee switch"},
    {"simbol": "AVAX", "nama_lengkap": "Avalanche", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume dipengaruhi oleh subnets seperti DeFi Kingdoms"},
    {"simbol": "ATOM", "nama_lengkap": "Cosmos", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume naik saat IBC bridge activity meningkat"},
    {"simbol": "LINK", "nama_lengkap": "Chainlink", "kategori": "Oracle", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume terkait dengan CCIP adoption (Cross-Chain Interoperability Protocol)"},
    {"simbol": "XLM", "nama_lengkap": "Stellar", "kategori": "Payment", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume dipicu oleh kemitraan remittance (contoh: MoneyGram)"},
    {"simbol": "BCH", "nama_lengkap": "Bitcoin Cash", "kategori": "Payment", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume naik saat halving cycle mendekat"},
    {"simbol": "ALGO", "nama_lengkap": "Algorand", "kategori": "Lapis 1", "volume_perdagangan": "Sedang-Tinggi", "potensi_katalis": "Volume terkait dengan governance rewards"},
    {"simbol": "FIL", "nama_lengkap": "Filecoin", "kategori": "Storage", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume dipengaruhi oleh NFT storage demand"},
    {"simbol": "TRX", "nama_lengkap": "TRON", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume naik saat stablecoin adoption di Asia"},
    {"simbol": "ETC", "nama_lengkap": "Ethereum Classic", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Volume dipicu oleh 51% attack fears"},
    {"simbol": "XMR", "nama_lengkap": "Monero", "kategori": "Privacy", "volume_perdagangan": "Sedang", "potensi_katalis": "Volume naik saat regulasi privacy coin ketat"},
    {"simbol": "THETA", "nama_lengkap": "Theta Network", "kategori": "Video", "volume_perdagangan": "Tinggi", "potensi_katalis": 'Volume terkait dengan partnership" (contoh: Sony, Samsung)"'},
    {"simbol": "CAKE", "nama_lengkap": "PancakeSwap", "kategori": "DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume naik saat IFO launches (Initial Farm Offerings)"},
    {"simbol": "VET", "nama_lengkap": "VeChain", "kategori": "Supply Chain", "volume_perdagangan": "Sedang", "potensi_katalis": "Volume dipicu oleh kemitraan korporat (contoh: Walmart China)"},
    {"simbol": "FTM", "nama_lengkap": "Fantom", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume terkait dengan DeFi TVL surge"},
    {"simbol": "EOS", "nama_lengkap": "EOS", "kategori": "Lapis 1", "volume_perdagangan": "Rendah-Sedang", "potensi_katalis": "Volume naik saat block producer elections"},
    {"simbol": "KSM", "nama_lengkap": "Kusama", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Volume dipengaruhi oleh Polkadot parachain auctions"},
    {"simbol": "XTZ", "nama_lengkap": "Tezos", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Volume naik saat baking rewards diumumkan"},
    {"simbol": "NEO", "nama_lengkap": "NEO", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Volume terkait dengan regulasi Tiongkok"},
    {"simbol": "DASH", "nama_lengkap": "Dash", "kategori": "Payment", "volume_perdagangan": "Rendah", "potensi_katalis": "Volume naik saat adopsi di negara hiperinflasi (contoh: Venezuela)"},
    {"simbol": "ZEC", "nama_lengkap": "Zcash", "kategori": "Privacy", "volume_perdagangan": "Rendah", "potensi_katalis": "Volume dipicu oleh halving events"},
    {"simbol": "MKR", "nama_lengkap": "Maker", "kategori": "DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume terkait dengan DAI stability fees"},
    {"simbol": "COMP", "nama_lengkap": "Compound", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Volume naik saat governance proposals"},
    {"simbol": "YFI", "nama_lengkap": "Yearn.Finance", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Volume dipicu oleh Andre Cronje tweets"},
    {"simbol": "SNX", "nama_lengkap": "Synthetix", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Volume terkait dengan synthetic asset demand"},
    {"simbol": "AAVE", "nama_lengkap": "Aave", "kategori": "DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume naik saat liquidity mining diluncurkan"},
    {"simbol": "SUSHI", "nama_lengkap": "SushiSwap", "kategori": "DeFi", "volume_perdagangan": "Sedang", "potensi_katalis": "Volume dipengaruhi oleh Onsen menu additions"},
    {"simbol": "CRV", "nama_lengkap": "Curve", "kategori": "DeFi", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume terkait dengan pool gauge wars"},
    {"simbol": "RUNE", "nama_lengkap": "THORChain", "kategori": "Cross-Chain", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume naik saat liquidity depth meningkat di aset utama"},
    {"simbol": "LDO", "nama_lengkap": "Lido DAO", "kategori": "Staking", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume dipicu oleh stETH depegging fears"},
    {"simbol": "GMX", "nama_lengkap": "GMX", "kategori": "Perp DEX", "volume_perdagangan": "Sangat Tinggi", "potensi_katalis": "Volume terkait dengan BTC/ETH volatility (>5% daily move = +200% volume)"},
    {"simbol": "DYDX", "nama_lengkap": "dYdX", "kategori": "Perp DEX", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume naik saat trading competitions"},
    {"simbol": "OP", "nama_lengkap": "Optimism", "kategori": "Lapis 2", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume terkait dengan OP token airdrops"},
    {"simbol": "ARB", "nama_lengkap": "Arbitrum", "kategori": "Lapis 2", "volume_perdagangan": "Tinggi", "potensi_katalis": "Volume dipicu oleh Arbitrum Odyssey"},
    {"simbol": "LUNA", "nama_lengkap": "Terra (v2)", "kategori": "Lapis 1", "volume_perdagangan": "Rendah", "potensi_katalis": "Volume naik saat community proposals (contoh: UST peg recovery)"},
    {"simbol": "FTT", "nama_lengkap": "FTX Token", "kategori": "Exchange", "volume_perdagangan": "Rendah", "potensi_katalis": "Volume hanya aktif saat berita FTX terkait"},
    {"simbol": "RAY", "nama_lengkap": "Raydium", "kategori": "DEX", "volume_perdagangan": "Sedang", "potensi_katalis": "Volume terkait dengan Solana NFT launches"},
    {"simbol": "HBAR", "nama_lengkap": "Hedera", "kategori": "Lapis 1", "volume_perdagangan": "Tinggi", "potensi_katalis": 'Volume dipicu oleh governance council news" (contoh: Google, IBM)"'},
    {"simbol": "ICP", "nama_lengkap": "Internet Computer", "kategori": "Lapis 1", "volume_perdagangan": "Sedang", "potensi_katalis": "Volume naik saat canister smart contract updates"},
]

# Hapus duplikat berdasarkan simbol
seen_symbols = set()
unique_coins = []
for coin in INTERNAL_COIN_LIST:
    symbol = coin['simbol']
    if symbol not in seen_symbols:
        unique_coins.append(coin)
        seen_symbols.add(symbol)
    # Jika simbol sudah ada, kita bisa memilih untuk menggabungkan informasi atau mengabaikannya.
    # Untuk saat ini, kita mengabaikan duplikat.

INTERNAL_COIN_LIST = unique_coins

# --- AKHIR DATA KOIN INTERNAL ---

class CryptoEcosystemScanner:
    """
    Memindai dan menganalisis ekosistem kripto berdasarkan daftar koin internal.
    Memfokuskan analisis berdasarkan kategori dan potensi katalis.
    """
    def __init__(self, orchestrator):
        """
        Inisialisasi Pemindai Ekosistem Kripto vFinal.
        Args:
            orchestrator: Instance dari ChimeraOrchestrator untuk akses ke API manager.
        """
        logging.info("Inisialisasi Pemindai Ekosistem Kripto vFinal (Internal Data)...")
        self.orchestrator = orchestrator
        # Asumsi: intelligence_aggregator tersedia melalui perception_system
        # atau diinisialisasi langsung jika diperlukan secara mandiri.
        # Untuk contoh ini, kita akan menggunakannya melalui orchestrator jika tersedia.
        self.intelligence_aggregator = getattr(self.orchestrator.perception_system, 'intelligence_aggregator', None)
        if not self.intelligence_aggregator:
            logging.warning("IntelligenceAggregator tidak ditemukan di PerceptionSystem. Fungsi scraping/pengambilan data eksternal akan terbatas.")
        logging.info("Pemindai Ekosistem Kripto vFinal berhasil diinisialisasi.")

    def _analyze_coin_by_category(self, coin_data: dict, perception_snapshot: dict):
        """
        Menganalisis koin berdasarkan kategorinya dan potensi katalisnya.
        Mensimulasikan pengambilan data spesifik.
        Args:
            coin_data (dict): Data koin dari daftar internal.
            perception_snapshot (dict): Snapshot persepsi pasar saat ini.
        Returns:
            dict: Hasil analisis spesifik untuk koin ini.
        """
        symbol = coin_data['simbol']
        full_name = coin_data['nama_lengkap']
        category = coin_data['kategori'].lower()
        catalyst = coin_data['potensi_katalis']
        volume_level = coin_data.get('volume_perdagangan', 'Rendah') # Tambahkan default
        logging.info(f"Menganalisis {symbol} ({full_name}) - Kategori: {category}, Katalis: {catalyst}, Volume: {volume_level}")
        
        analysis_result = {
            'coin_info': coin_data,
            'analysis_timestamp': datetime.utcnow().isoformat() + 'Z',
            'category_insights': {},
            'catalyst_insights': {},
            'simulated_market_data': {}, # Placeholder untuk data harga simulasi
            'onchain_signals': {}, # Placeholder untuk sinyal on-chain
            'derivatives_signals': {}, # Placeholder untuk sinyal derivatif
            'sentiment_signals': {}, # Placeholder untuk sinyal sentimen
            'macro_geopolitical_signals': {}, # Placeholder untuk sinyal makro/geopolitik
            'technical_indicators': {}, # Placeholder untuk indikator teknis
            'mathematical_analysis': {}, # Placeholder untuk analisis matematika
            'warfare_principles': {}, # Placeholder untuk prinsip strategi perang
            'futuristic_analysis': {}, # Placeholder untuk analisis futuristik
            'key_levels': {}, # Placeholder untuk level kunci
            'timing_analysis': {}, # Placeholder untuk analisis timing
            'risk_management': {} # Placeholder untuk manajemen risiko
        }

        # --- Simulasi Pengambilan Data Pasar (menggantikan IntelligenceAggregator untuk demo) ---
        # Dalam implementasi penuh, ini akan memanggil self.intelligence_aggregator
        try:
            # Simulasi jitter kecil untuk API call
            time.sleep(random.uniform(0.05, 0.2))
            # Simulasi pengambilan harga (dalam implementasi nyata: intelligence_aggregator.get_market_price)
            simulated_price = round(random.uniform(1000, 50000), 2) if symbol in ['BTC', 'ETH'] else round(random.uniform(0.001, 100), 4)
            analysis_result['simulated_market_data']['price'] = simulated_price
            analysis_result['simulated_market_data']['change_24h'] = round(random.uniform(-5, 5), 2)
            analysis_result['simulated_market_data']['volume_24h'] = round(simulated_price * random.uniform(1000000, 100000000), 2) # Simulasi
            logging.debug(f"Data pasar tersimulasi untuk {symbol}: ${simulated_price}")
        except Exception as e:
            logging.warning(f"Simulasi pengambilan data pasar untuk {symbol} gagal: {e}")
            analysis_result['simulated_market_data']['price'] = None

        # --- Analisis Berdasarkan Kategori ---
        category_insights = {}
        if 'lapis 1' in category or 'layer 1' in category:
            category_insights['focus'] = 'Analisis teknologi dasar, skalabilitas, dan adopsi pengembang.'
            category_insights['metrics'] = ['hashrate', 'active_addresses', 'developer_activity', 'block_time', 'gas_used']
            # Simulasi sinyal on-chain spesifik
            analysis_result['onchain_signals']['hashrate'] = round(random.uniform(100000, 500000), 2)
            analysis_result['onchain_signals']['active_addresses'] = int(random.uniform(10000, 100000))
        elif 'lapis 2' in category or 'layer 2' in category:
            category_insights['focus'] = 'Analisis throughput, biaya transaksi, dan adopsi aplikasi.'
            category_insights['metrics'] = ['tps', 'avg_gas_price', 'batch_size', 'sequencer_activity']
            analysis_result['onchain_signals']['tps'] = round(random.uniform(100, 5000), 2)
            analysis_result['onchain_signals']['avg_gas_price'] = round(random.uniform(10, 100), 2)
        elif 'defi' in category:
            category_insights['focus'] = 'Analisis metrik DeFi seperti TVL, yield, dan aktivitas protokol.'
            category_insights['metrics'] = ['tvl', 'apy/apr', 'total_debt_issued', 'swap_volume']
            analysis_result['onchain_signals']['tvl'] = round(random.uniform(1000000, 100000000), 2)
            analysis_result['onchain_signals']['apy'] = round(random.uniform(1, 20), 2)
        elif 'ai' in category or 'artificial intelligence' in category:
            category_insights['focus'] = 'Analisis perkembangan jaringan AI, penggunaan token, dan mitra.'
            category_insights['metrics'] = ['network_utilization', 'data_processed', 'active_agents', 'model_performance']
            analysis_result['onchain_signals']['network_utilization'] = round(random.uniform(10, 90), 2)
            analysis_result['onchain_signals']['active_agents'] = int(random.uniform(100, 10000))
        elif 'memecoin' in category:
            category_insights['focus'] = 'Analisis sentimen media sosial, volume perdagangan, dan tren meme.'
            category_insights['metrics'] = ['social_volume', 'sentiment_score', 'unique_wallets', 'meme_virality_index']
            analysis_result['sentiment_signals']['social_volume'] = int(random.uniform(10000, 1000000))
            analysis_result['sentiment_signals']['sentiment_score'] = round(random.uniform(-1, 1), 2)
        elif 'payments' in category:
             category_insights['focus'] = 'Analisis adopsi pembayaran, partnership ritel, dan volume transaksi.'
             category_insights['metrics'] = ['merchant_count', 'transaction_volume', 'average_tx_value', 'payment_success_rate']
             analysis_result['onchain_signals']['merchant_count'] = int(random.uniform(1000, 100000))
             analysis_result['onchain_signals']['transaction_volume'] = round(random.uniform(1000000, 100000000), 2)
        elif 'metaverse' in category:
             category_insights['focus'] = 'Analisis aktivitas pengguna di platform, penjualan NFT, dan investasi.'
             category_insights['metrics'] = ['daily_active_users', 'nft_sales_volume', 'land_price_index', 'virtual_asset_transactions']
             analysis_result['onchain_signals']['daily_active_users'] = int(random.uniform(1000, 100000))
             analysis_result['onchain_signals']['nft_sales_volume'] = round(random.uniform(100000, 10000000), 2)
        elif 'oracle' in category:
             category_insights['focus'] = 'Analisis jumlah permintaan data, uptime, dan kepercayaan protokol.'
             category_insights['metrics'] = ['data_requests', 'uptime_percentage', 'secure_agreements', 'feed_diversity']
             analysis_result['onchain_signals']['data_requests'] = int(random.uniform(10000, 1000000))
             analysis_result['onchain_signals']['uptime_percentage'] = round(random.uniform(99, 100), 2)
        elif 'gaming' in category:
             category_insights['focus'] = 'Analisis aktivitas pemain, NFT marketplace, dan tokenomics.'
             category_insights['metrics'] = ['daily_active_users', 'nft_trading_volume', 'token_burn_rate', 'in_game_asset_value']
             analysis_result['onchain_signals']['daily_active_users'] = int(random.uniform(1000, 100000))
             analysis_result['onchain_signals']['nft_trading_volume'] = round(random.uniform(100000, 10000000), 2)
        elif 'nft' in category:
             category_insights['focus'] = 'Analisis volume perdagangan NFT, marketplace activity, dan floor price.'
             category_insights['metrics'] = ['nft_sales_volume', 'marketplace_activity', 'floor_price', 'unique_collectors']
             analysis_result['onchain_signals']['nft_sales_volume'] = round(random.uniform(100000, 10000000), 2)
             analysis_result['onchain_signals']['floor_price'] = round(random.uniform(0.01, 10), 4)
        elif 'privacy' in category:
             category_insights['focus'] = 'Analisis adopsi privasi, network hashrate, dan regulatory sentiment.'
             category_insights['metrics'] = ['network_hashrate', 'mixing_volume', 'regulatory_news', 'anonymity_set_size']
             analysis_result['onchain_signals']['network_hashrate'] = round(random.uniform(10000, 1000000), 2)
             analysis_result['sentiment_signals']['regulatory_sentiment'] = round(random.uniform(-1, 1), 2)
        elif 'staking' in category:
             category_insights['focus'] = 'Analisis APR, jumlah staking, dan likuiditas token staking.'
             category_insights['metrics'] = ['staking_apr', 'total_staked', 'liquid_staking_supply', 'validator_distribution']
             analysis_result['onchain_signals']['staking_apr'] = round(random.uniform(5, 20), 2)
             analysis_result['onchain_signals']['total_staked'] = round(random.uniform(1000000, 100000000), 2)
        elif 'infrastructure' in category or 'interop' in category or 'interoperability' in category:
             category_insights['focus'] = 'Analisis adopsi jaringan, jumlah validator, dan integrasi protokol.'
             category_insights['metrics'] = ['network_adoption', 'validator_count', 'protocol_integrations', 'cross_chain_tx_volume']
             analysis_result['onchain_signals']['validator_count'] = int(random.uniform(50, 1000))
             analysis_result['onchain_signals']['cross_chain_tx_volume'] = round(random.uniform(1000000, 50000000), 2)
        elif 'storage' in category:
             category_insights['focus'] = 'Analisis kapasitas penyimpanan terpakai, jumlah penyedia, dan permintaan data.'
             category_insights['metrics'] = ['storage_used', 'storage_providers', 'data_requests', 'retrieval_success_rate']
             analysis_result['onchain_signals']['storage_used'] = round(random.uniform(1000000, 1000000000), 2) # TB
             analysis_result['onchain_signals']['storage_providers'] = int(random.uniform(100, 10000))
        elif 'video' in category:
             category_insights['focus'] = 'Analisis bandwidth yang digunakan, jumlah penonton, dan kemitraan konten.'
             category_insights['metrics'] = ['bandwidth_used', 'viewer_count', 'content_partnerships', 'stream_quality']
             analysis_result['onchain_signals']['bandwidth_used'] = round(random.uniform(1000000, 100000000), 2) # GB
             analysis_result['onchain_signals']['viewer_count'] = int(random.uniform(10000, 1000000))
        elif 'supply chain' in category:
             category_insights['focus'] = 'Analisis jumlah produk yang dilacak, mitra korporat, dan volume transaksi.'
             category_insights['metrics'] = ['products_tracked', 'corporate_partners', 'transaction_volume', 'traceability_accuracy']
             analysis_result['onchain_signals']['products_tracked'] = int(random.uniform(100000, 10000000))
             analysis_result['onchain_signals']['corporate_partners'] = int(random.uniform(10, 1000))
        elif 'exchange token' in category:
             category_insights['focus'] = 'Analisis volume perdagangan di exchange, jumlah pengguna aktif, dan program burn.'
             category_insights['metrics'] = ['exchange_volume', 'active_users', 'tokens_burned', 'fee_discount_usage']
             analysis_result['onchain_signals']['exchange_volume'] = round(random.uniform(100000000, 1000000000), 2)
             analysis_result['onchain_signals']['active_users'] = int(random.uniform(100000, 10000000))
        elif 'fan token' in category:
             category_insights['focus'] = 'Analisis engagement fans, hasil pertandingan tim, dan aktivitas di platform klub.'
             category_insights['metrics'] = ['fan_engagement_score', 'team_performance', 'club_platform_activity', 'token_utilization']
             analysis_result['sentiment_signals']['fan_engagement_score'] = round(random.uniform(0, 100), 2)
             analysis_result['sentiment_signals']['team_performance'] = round(random.uniform(0, 100), 2) # Simulasi
        elif 'rwa' in category or 'real world assets' in category:
             category_insights['focus'] = 'Analisis nilai aset yang di-tokenisasi, regulasi, dan adopsi institusional.'
             category_insights['metrics'] = ['rwa_value_tokenized', 'regulatory_compliance_score', 'institutional_adoptions', 'asset_diversification']
             analysis_result['macro_geopolitical_signals']['regulatory_compliance_score'] = round(random.uniform(0, 100), 2)
             analysis_result['onchain_signals']['rwa_value_tokenized'] = round(random.uniform(10000000, 1000000000), 2)
        elif 'bitcoin layer' in category or 'btc layer' in category:
             category_insights['focus'] = 'Analisis keterkaitan dengan Bitcoin, security model, dan adopsi spesifik BTC.'
             category_insights['metrics'] = ['btc_security_utilization', 'btc_locked_value', 'btc_transaction_finality', 'wrapped_btc_supply']
             analysis_result['onchain_signals']['btc_locked_value'] = round(random.uniform(10000, 1000000), 2)
             analysis_result['onchain_signals']['wrapped_btc_supply'] = round(random.uniform(100000, 10000000), 2)
        elif 'dao' in category:
             category_insights['focus'] = 'Analisis partisipasi voting, jumlah proposal, dan nilai treasury.'
             category_insights['metrics'] = ['voting_participation', 'proposals_submitted', 'treasury_value', 'active_proposers']
             analysis_result['onchain_signals']['voting_participation'] = round(random.uniform(10, 90), 2) # %
             analysis_result['onchain_signals']['treasury_value'] = round(random.uniform(1000000, 100000000), 2)
        elif 'energy' in category:
             category_insights['focus'] = 'Analisis penggunaan energi terbarukan, efisiensi jaringan, dan dampak lingkungan.'
             category_insights['metrics'] = ['renewable_energy_usage', 'network_energy_efficiency', 'carbon_footprint', 'green_energy_partnerships']
             analysis_result['onchain_signals']['renewable_energy_usage'] = round(random.uniform(20, 100), 2) # %
             analysis_result['macro_geopolitical_signals']['carbon_footprint'] = round(random.uniform(100, 10000), 2) # Ton CO2
        elif 'music' in category:
             category_insights['focus'] = 'Analisis jumlah artis yang bermigrasi, volume penjualan musik NFT, dan engagement penggemar.'
             category_insights['metrics'] = ['migrating_artists', 'music_nft_sales', 'fan_engagement', 'royalty_distribution']
             analysis_result['onchain_signals']['music_nft_sales'] = round(random.uniform(10000, 1000000), 2)
             analysis_result['sentiment_signals']['fan_engagement'] = round(random.uniform(0, 100), 2)
        elif 'identity' in category:
             category_insights['focus'] = 'Analisis adopsi identitas terdesentralisasi, jumlah verifikasi, dan integrasi dengan aplikasi.'
             category_insights['metrics'] = ['did_adoptions', 'verifications_completed', 'app_integrations', 'identity_security_score']
             analysis_result['onchain_signals']['did_adoptions'] = int(random.uniform(10000, 1000000))
             analysis_result['onchain_signals']['verifications_completed'] = int(random.uniform(100000, 10000000))
        elif 'iot' in category or 'internet of things' in category:
             category_insights['focus'] = 'Analisis jumlah perangkat yang terhubung, volume data yang diproses, dan use case industri.'
             category_insights['metrics'] = ['connected_devices', 'data_volume_processed', 'industrial_use_cases', 'device_security_level']
             analysis_result['onchain_signals']['connected_devices'] = int(random.uniform(100000, 100000000))
             analysis_result['onchain_signals']['data_volume_processed'] = round(random.uniform(1000000, 1000000000), 2) # GB
        elif 'telecom' in category:
             category_insights['focus'] = 'Analisis kapasitas bandwidth yang disediakan, jumlah pengguna, dan kemitraan operator.'
             category_insights['metrics'] = ['bandwidth_capacity', 'user_base', 'operator_partnerships', 'data_transaction_fees']
             analysis_result['onchain_signals']['user_base'] = int(random.uniform(100000, 10000000))
             analysis_result['onchain_signals']['bandwidth_capacity'] = round(random.uniform(1000000, 100000000), 2) # GB
        elif 'data' in category:
             category_insights['focus'] = 'Analisis volume data yang dijual/beli, jumlah penyedia data, dan kualitas data.'
             category_insights['metrics'] = ['data_trading_volume', 'data_providers', 'data_quality_index', 'data_monetization_models']
             analysis_result['onchain_signals']['data_trading_volume'] = round(random.uniform(1000000, 100000000), 2)
             analysis_result['onchain_signals']['data_providers'] = int(random.uniform(100, 10000))
        elif 'synthetic assets' in category:
             category_insights['focus'] = 'Analisis total nilai aset sintetis yang diterbitkan, leverage yang digunakan, dan likuiditas pasar.'
             category_insights['metrics'] = ['synthetic_assets_value', 'average_leverage', 'market_liquidity', 'collateral_types']
             analysis_result['onchain_signals']['synthetic_assets_value'] = round(random.uniform(10000000, 1000000000), 2)
             analysis_result['onchain_signals']['average_leverage'] = round(random.uniform(1, 50), 2)
        elif 'ux' in category or 'user experience' in category:
             category_insights['focus'] = 'Analisis kemudahan penggunaan, adopsi wallet, dan integrasi dengan platform lain.'
             category_insights['metrics'] = ['ease_of_use_score', 'wallet_adoptions', 'platform_integrations', 'user_onboarding_rate']
             analysis_result['sentiment_signals']['ease_of_use_score'] = round(random.uniform(1, 10), 2)
             analysis_result['onchain_signals']['wallet_adoptions'] = int(random.uniform(10000, 1000000))
        elif 'funding' in category or 'public goods' in category:
             category_insights['focus'] = 'Analisis jumlah dana yang didistribusikan, proyek yang didanai, dan efektivitas mekanisme funding.'
             category_insights['metrics'] = ['funds_distributed', 'projects_funded', 'funding_efficiency', 'community_participation']
             analysis_result['onchain_signals']['funds_distributed'] = round(random.uniform(1000000, 100000000), 2)
             analysis_result['onchain_signals']['projects_funded'] = int(random.uniform(100, 10000))
        elif 'marketplace' in category:
             category_insights['focus'] = 'Analisis volume transaksi, jumlah penjual/penawar, dan reputasi pengguna.'
             category_insights['metrics'] = ['transaction_volume', 'sellers/bidders', 'user_reputation_scores', 'dispute_resolution_rate']
             analysis_result['onchain_signals']['transaction_volume'] = round(random.uniform(100000, 10000000), 2) # Asumsi key typo di sini, perlu fix jika ada
             analysis_result['onchain_signals']['sellers/bidders'] = int(random.uniform(1000, 100000))
        elif 'liquidity' in category:
             category_insights['focus'] = 'Analisis depth order book, spread, dan volume perdagangan cross-exchange.'
             category_insights['metrics'] = ['order_book_depth', 'bid_ask_spread', 'cross_exchange_volume', 'liquidity_provider_count']
             analysis_result['technical_indicators']['order_book_depth'] = round(random.uniform(1000000, 100000000), 2)
             analysis_result['technical_indicators']['bid_ask_spread'] = round(random.uniform(0.1, 5), 2) # Basis points
        elif 'lending' in category:
             category_insights['focus'] = 'Analisis total pinjaman yang diberikan, tingkat bunga, dan rasio pinjaman terhadap nilai kolateral.'
             category_insights['metrics'] = ['total_loans_issued', 'interest_rates', 'ltv_ratios', 'default_rates']
             analysis_result['onchain_signals']['total_loans_issued'] = round(random.uniform(10000000, 1000000000), 2)
             analysis_result['onchain_signals']['interest_rates'] = round(random.uniform(1, 20), 2) # %
        elif 'dex' in category or 'dex aggregator' in category:
             category_insights['focus'] = 'Analisis volume swap, jumlah pool likuiditas, dan biaya protokol.'
             category_insights['metrics'] = ['swap_volume', 'liquidity_pools', 'protocol_fees', 'slippage_rates']
             analysis_result['onchain_signals']['swap_volume'] = round(random.uniform(10000000, 1000000000), 2)
             analysis_result['onchain_signals']['liquidity_pools'] = int(random.uniform(100, 10000))
        elif 'perp dex' in category or 'perpetual dex' in category:
             category_insights['focus'] = 'Analisis volume perdagangan perpetual, funding rates, dan open interest.'
             category_insights['metrics'] = ['perp_trading_volume', 'funding_rates', 'open_interest', 'liquidation_events']
             analysis_result['derivatives_signals']['perp_trading_volume'] = round(random.uniform(100000000, 10000000000), 2)
             analysis_result['derivatives_signals']['funding_rates'] = round(random.uniform(-0.1, 0.1), 4) # %
             analysis_result['derivatives_signals']['open_interest'] = round(random.uniform(10000000, 1000000000), 2)
        elif 'stablecoin' in category:
             category_insights['focus'] = 'Analisis kapitalisasi, mekanisme peg, dan cadangan yang mendukung.'
             category_insights['metrics'] = ['market_cap', 'peg_mechanism', 'reserves/backing', 'redemption_rate']
             analysis_result['onchain_signals']['market_cap'] = round(random.uniform(100000000, 10000000000), 2)
             analysis_result['onchain_signals']['redemption_rate'] = round(random.uniform(0.99, 1.01), 4)
        elif 'indexing' in category:
             category_insights['focus'] = 'Analisis jumlah query yang diproses, jumlah subgraph/dataset yang diindeks, dan uptime layanan.'
             category_insights['metrics'] = ['queries_processed', 'subgraphs/datasets_indexed', 'service_uptime', 'query_response_time']
             analysis_result['onchain_signals']['queries_processed'] = int(random.uniform(1000000, 100000000))
             analysis_result['onchain_signals']['subgraphs/datasets_indexed'] = int(random.uniform(1000, 100000))
        elif 'depin' in category or 'decentralized physical infrastructure' in category:
             category_insights['focus'] = 'Analisis jumlah node/hardware yang berpartisipasi, uptime jaringan, dan nilai token yang dikunci.'
             category_insights['metrics'] = ['participating_nodes', 'network_uptime', 'token_locked_value', 'resource_provisioned']
             analysis_result['onchain_signals']['participating_nodes'] = int(random.uniform(1000, 1000000))
             analysis_result['onchain_signals']['network_uptime'] = round(random.uniform(99, 100), 2) # %
        elif 'modular' in category:
             category_insights['focus'] = 'Analisis jumlah rollups/appchains yang terhubung, throughput yang ditangani, dan interoperabilitas.'
             category_insights['metrics'] = ['connected_rollups/appchains', 'handled_throughput', 'interoperability_score', 'modular_components_used']
             analysis_result['onchain_signals']['connected_rollups/appchains'] = int(random.uniform(10, 1000))
             analysis_result['onchain_signals']['handled_throughput'] = round(random.uniform(1000, 100000), 2) # TPS
        elif 'zero-knowledge' in category or 'zk' in category:
             category_insights['focus'] = 'Analisis jumlah transaksi ZK yang diproses, waktu verifikasi, dan adopsi aplikasi ZK.'
             category_insights['metrics'] = ['zk_transactions_processed', 'verification_time', 'zk_app_adoptions', 'proof_size']
             analysis_result['onchain_signals']['zk_transactions_processed'] = int(random.uniform(10000, 10000000))
             analysis_result['onchain_signals']['verification_time'] = round(random.uniform(1, 1000), 2) # ms
        elif 'move' in category:
             category_insights['focus'] = 'Analisis adopsi bahasa Move, jumlah modul yang dideploy, dan keamanan kontrak.'
             category_insights['metrics'] = ['move_adoptions', 'modules_deployed', 'contract_security_audits', 'parallel_execution_efficiency']
             analysis_result['onchain_signals']['move_adoptions'] = int(random.uniform(1000, 100000))
             analysis_result['onchain_signals']['modules_deployed'] = int(random.uniform(10000, 1000000))
        elif 'enterprise' in category:
             category_insights['focus'] = 'Analisis jumlah kemitraan enterprise, penggunaan dalam solusi B2B, dan regulasi yang sesuai.'
             category_insights['metrics'] = ['enterprise_partnerships', 'b2b_solution_usage', 'regulatory_compliance', 'enterprise_transaction_volume']
             analysis_result['macro_geopolitical_signals']['enterprise_partnerships'] = int(random.uniform(10, 1000))
             analysis_result['onchain_signals']['enterprise_transaction_volume'] = round(random.uniform(1000000, 100000000), 2)
        elif 'platform' in category:
             category_insights['focus'] = 'Analisis jumlah dApp yang berjalan, aktivitas pengguna di platform, dan ekosistem pengembang.'
             category_insights['metrics'] = ['dapps_running', 'platform_user_activity', 'developer_ecosystem', 'smart_contract_deployments']
             analysis_result['onchain_signals']['dapps_running'] = int(random.uniform(100, 10000))
             analysis_result['onchain_signals']['platform_user_activity'] = int(random.uniform(10000, 1000000))
        elif 'dag' in category or 'directed acyclic graph' in category:
             category_insights['focus'] = 'Analisis throughput transaksi, finality time, dan struktur jaringan DAG.'
             category_insights['metrics'] = ['transaction_throughput', 'finality_time', 'dag_structure_efficiency', 'confirmation_latency']
             analysis_result['onchain_signals']['transaction_throughput'] = round(random.uniform(1000, 100000), 2) # TPS
             analysis_result['onchain_signals']['finality_time'] = round(random.uniform(1, 60), 2) # seconds
        elif 'utxo' in category:
             category_insights['focus'] = 'Analisis jumlah transaksi UTXO, ukuran mempool, dan efisiensi penggunaan UTXO set.'
             category_insights['metrics'] = ['utxo_transactions', 'mempool_size', 'utxo_set_efficiency', 'average_utxos_per_transaction']
             analysis_result['onchain_signals']['utxo_transactions'] = int(random.uniform(100000, 10000000))
             analysis_result['onchain_signals']['mempool_size'] = round(random.uniform(100, 10000), 2) # MB
        elif 'naming service' in category:
             category_insights['focus'] = 'Analisis jumlah nama/domain yang terdaftar, adopsi di dApps, dan keamanan resolver.'
             category_insights['metrics'] = ['names_registered', 'dapp_adoptions', 'resolver_security', 'renewal_rates']
             analysis_result['onchain_signals']['names_registered'] = int(random.uniform(100000, 10000000))
             analysis_result['onchain_signals']['dapp_adoptions'] = int(random.uniform(100, 10000))
        elif 'code collaboration' in category:
             category_insights['focus'] = 'Analisis jumlah proyek open-source, kontributor aktif, dan kode yang direview.'
             category_insights['metrics'] = ['open_source_projects', 'active_contributors', 'code_reviewed', 'merge_request_velocity']
             analysis_result['onchain_signals']['open_source_projects'] = int(random.uniform(100, 10000))
             analysis_result['onchain_signals']['active_contributors'] = int(random.uniform(1000, 100000))
        elif 'socialfi' in category or 'social finance' in category:
             category_insights['focus'] = 'Analisis engagement pengguna, jumlah creator yang bergabung, dan volume transaksi sosial.'
             category_insights['metrics'] = ['user_engagement', 'creators_joined', 'social_transaction_volume', 'content_monetization']
             analysis_result['sentiment_signals']['user_engagement'] = round(random.uniform(0, 100), 2)
             analysis_result['onchain_signals']['creators_joined'] = int(random.uniform(1000, 100000))
        elif 'ed-tech' in category or 'education technology' in category:
             category_insights['focus'] = 'Analisis jumlah pengguna yang teredukasi, kursus yang diselesaikan, dan adopsi token dalam pembelajaran.'
             category_insights['metrics'] = ['users_educated', 'courses_completed', 'token_adoptions_in_learning', 'educational_outcomes']
             analysis_result['onchain_signals']['users_educated'] = int(random.uniform(10000, 1000000))
             analysis_result['onchain_signals']['courses_completed'] = int(random.uniform(1000, 100000))
        elif 'move-to-earn' in category:
             category_insights['focus'] = 'Analisis jumlah pengguna aktif, jarak/tempo yang dilacak, dan ekonomi token berbasis aktivitas fisik.'
             category_insights['metrics'] = ['active_users', 'distance_tracked', 'token_economy_activity', 'fitness_goal_achievements']
             analysis_result['onchain_signals']['active_users'] = int(random.uniform(10000, 1000000))
             analysis_result['onchain_signals']['distance_tracked'] = round(random.uniform(1000000, 100000000), 2) # km
        elif 'cloud' in category or 'decentralized cloud' in category:
             category_insights['focus'] = 'Analisis kapasitas penyimpanan komputasi yang disediakan, jumlah node, dan uptime layanan.'
             category_insights['metrics'] = ['computing_storage_capacity', 'node_count', 'service_uptime', 'resource_allocation_efficiency']
             analysis_result['onchain_signals']['computing_storage_capacity'] = round(random.uniform(1000000, 1000000000), 2) # GB
             analysis_result['onchain_signals']['node_count'] = int(random.uniform(1000, 1000000))
        elif 'yield' in category or 'yield aggregator' in category:
             category_insights['focus'] = 'Analisis APY yang ditawarkan, strategi yield yang digunakan, dan total aset yang dikelola.'
             category_insights['metrics'] = ['apy_offered', 'yield_strategies', 'total_assets_managed', 'strategy_diversification']
             analysis_result['onchain_signals']['apy_offered'] = round(random.uniform(5, 50), 2) # %
             analysis_result['onchain_signals']['total_assets_managed'] = round(random.uniform(10000000, 1000000000), 2)
        elif 'auction' in category:
             category_insights['focus'] = 'Analisis volume lelang, jumlah peserta, dan efisiensi mekanisme lelang.'
             category_insights['metrics'] = ['auction_volume', 'participant_count', 'auction_efficiency', 'bid_distribution']
             analysis_result['onchain_signals']['auction_volume'] = round(random.uniform(1000000, 100000000), 2)
             analysis_result['onchain_signals']['participant_count'] = int(random.uniform(100, 10000))
        elif 'credentials' in category:
             category_insights['focus'] = 'Analisis jumlah kredensial yang diterbitkan, verifikasi yang dilakukan, dan adopsi di berbagai platform.'
             category_insights['metrics'] = ['credentials_issued', 'verifications_performed', 'platform_adoptions', 'credential_types']
             analysis_result['onchain_signals']['credentials_issued'] = int(random.uniform(100000, 10000000))
             analysis_result['onchain_signals']['verifications_performed'] = int(random.uniform(1000000, 100000000))
        elif 'wallet' in category:
             category_insights['focus'] = 'Analisis jumlah pengguna wallet, volume transaksi, dan fitur keamanan yang diadopsi.'
             category_insights['metrics'] = ['wallet_users', 'transaction_volume', 'security_features_adopted', 'multi_chain_support']
             analysis_result['onchain_signals']['wallet_users'] = int(random.uniform(100000, 10000000))
             analysis_result['onchain_signals']['transaction_volume'] = round(random.uniform(10000000, 1000000000), 2)
        elif 'computation' in category:
             category_insights['focus'] = 'Analisis permintaan komputasi, jumlah node penyedia, dan waktu pemrosesan.'
             category_insights['metrics'] = ['compute_demand', 'provider_nodes', 'processing_time', 'computational_efficiency']
             analysis_result['onchain_signals']['compute_demand'] = round(random.uniform(1000000, 100000000), 2) # Unit komputasi
             analysis_result['onchain_signals']['provider_nodes'] = int(random.uniform(100, 10000))
        elif 'middleware' in category:
             category_insights['focus'] = 'Analisis throughput pesan yang dirouting, latency, dan keandalan layanan middleware.'
             category_insights['metrics'] = ['message_throughput', 'routing_latency', 'service_reliability', 'protocol_interoperability']
             analysis_result['onchain_signals']['message_throughput'] = round(random.uniform(1000, 100000), 2) # msg/sec
             analysis_result['onchain_signals']['routing_latency'] = round(random.uniform(10, 1000), 2) # ms
        else:
            category_insights['focus'] = 'Analisis umum berdasarkan volume dan volatilitas.'
            category_insights['metrics'] = ['price_correlation', 'volatility_index', 'market_cap_rank', 'liquidity_depth']
            analysis_result['technical_indicators']['volatility_index'] = round(random.uniform(20, 80), 2)
            analysis_result['technical_indicators']['price_correlation'] = round(random.uniform(-1, 1), 2)

        analysis_result['category_insights'] = category_insights

        # --- Analisis Berdasarkan Potensi Katalis ---
        catalyst_insights = {}
        # --- Macro Catalysts ---
        if 'institusional' in catalyst.lower() or 'etf' in catalyst.lower() or 'institutional' in catalyst.lower():
            catalyst_insights['type'] = 'Macro Catalyst'
            catalyst_insights['action'] = 'Monitor berita regulasi, laporan ETF, dan pergerakan dana institusional.'
            # Simulasi sinyal makro
            analysis_result['macro_geopolitical_signals']['etf_inflows'] = round(random.uniform(0, 100000000), 2) # Simulasi
            analysis_result['macro_geopolitical_signals']['institutional_adoptions'] = int(random.uniform(10, 1000)) # Simulasi
        elif 'adoption' in catalyst.lower() or 'partnership' in catalyst.lower() or 'integration' in catalyst.lower() or 'launch' in catalyst.lower():
             catalyst_insights['type'] = 'Adoption Catalyst'
             catalyst_insights['action'] = 'Cari berita resmi tentang kemitraan, integrasi, atau penggunaan baru.'
             analysis_result['onchain_signals']['adoption_rate'] = round(random.uniform(1, 20), 2) # % weekly growth
        # --- Regulatory Catalysts ---
        elif 'legal' in catalyst.lower() or 'resolution' in catalyst.lower() or 'regulation' in catalyst.lower() or 'ban' in catalyst.lower() or 'compliance' in catalyst.lower():
             catalyst_insights['type'] = 'Regulatory Catalyst'
             catalyst_insights['action'] = 'Pantau pengadilan, klarifikasi hukum, dan dampak terhadap harga.'
             analysis_result['macro_geopolitical_signals']['regulatory_clarity_score'] = round(random.uniform(0, 100), 2)
             analysis_result['sentiment_signals']['regulatory_sentiment'] = round(random.uniform(-1, 1), 2)
        # --- Social Catalysts ---
        elif 'meme' in catalyst.lower() or 'virality' in catalyst.lower() or 'tweets' in catalyst.lower() or 'social' in catalyst.lower() or 'community' in catalyst.lower() or 'influencer' in catalyst.lower():
             catalyst_insights['type'] = 'Social Catalyst'
             catalyst_insights['action'] = 'Analisis tren Twitter/X, forum Reddit, dan aktivitas influencer.'
             analysis_result['sentiment_signals']['social_volume'] = int(random.uniform(100000, 10000000))
             analysis_result['sentiment_signals']['sentiment_score'] = round(random.uniform(-1, 1), 2)
        # --- Technology Catalysts ---
        elif 'ai breakthrough' in catalyst.lower() or 'network mining' in catalyst.lower() or 'upgrade' in catalyst.lower() or 'update' in catalyst.lower() or 'innovation' in catalyst.lower() or 'zk' in catalyst.lower() or 'layer' in catalyst.lower() or 'consensus' in catalyst.lower():
             catalyst_insights['type'] = 'Technology Catalyst'
             catalyst_insights['action'] = 'Ikuti perkembangan teknis proyek, paper penelitian, dan update node.'
             analysis_result['onchain_signals']['tech_development_score'] = round(random.uniform(0, 100), 2) # Simulasi
        # --- Supply Catalysts ---
        elif 'burn' in catalyst.lower() or 'supply' in catalyst.lower() or 'halving' in catalyst.lower() or 'tokenomics' in catalyst.lower():
             catalyst_insights['type'] = 'Supply Catalyst'
             catalyst_insights['action'] = 'Hitung jumlah token yang dibakar dan dampak deflasi terhadap harga.'
             analysis_result['onchain_signals']['burn_rate'] = round(random.uniform(0, 1000000), 2) # tokens/day
             analysis_result['onchain_signals']['supply_change_rate'] = round(random.uniform(-5, 5), 2) # % annual
        # --- Gaming/NFT Catalysts ---
        elif 'gaming' in catalyst.lower() or 'nft' in catalyst.lower() or 'scholarship' in catalyst.lower() or 'metaverse' in catalyst.lower() or 'game' in catalyst.lower() or 'play' in catalyst.lower():
             catalyst_insights['type'] = 'Gaming/NFT Catalyst'
             catalyst_insights['action'] = 'Monitor aktivitas game, penjualan NFT, dan ekonomi token.'
             analysis_result['onchain_signals']['nft_sales_volume'] = round(random.uniform(100000, 10000000), 2) # Simulasi
             analysis_result['onchain_signals']['game_active_users'] = int(random.uniform(1000, 1000000)) # Simulasi
        # --- DeFi Yield Catalysts ---
        elif 'yield' in catalyst.lower() or 'lending' in catalyst.lower() or 'tvl' in catalyst.lower() or 'apy' in catalyst.lower() or 'apr' in catalyst.lower() or 'liquidity' in catalyst.lower():
             catalyst_insights['type'] = 'DeFi Yield Catalyst'
             catalyst_insights['action'] = 'Analisis APR/APY, Total Value Locked (TVL), dan protokol terkait.'
             analysis_result['onchain_signals']['tvl_growth'] = round(random.uniform(-10, 50), 2) # % weekly
             analysis_result['onchain_signals']['yield_apr'] = round(random.uniform(1, 50), 2) # %
        # --- Fan Token/Sports Catalysts ---
        elif 'sports' in catalyst.lower() or 'fan token' in catalyst.lower() or 'matches' in catalyst.lower() or 'championship' in catalyst.lower() or 'tournament' in catalyst.lower():
             catalyst_insights['type'] = 'Fan Token/Sports Catalyst'
             catalyst_insights['action'] = 'Pantau jadwal pertandingan, aktivitas fan, dan kemitraan klub.'
             analysis_result['sentiment_signals']['fan_activity_score'] = round(random.uniform(0, 100), 2)
        # --- Price/Market Catalysts ---
        elif 'volatility' in catalyst.lower() or 'price' in catalyst.lower() or 'liquidation' in catalyst.lower() or 'funding' in catalyst.lower():
             catalyst_insights['type'] = 'Price/Market Catalyst'
             catalyst_insights['action'] = 'Analisis volatilitas harga, cluster liquidation, dan funding rates.'
             analysis_result['technical_indicators']['volatility'] = round(random.uniform(2, 20), 2) # %
             analysis_result['derivatives_signals']['funding_rate'] = round(random.uniform(-0.1, 0.1), 4) # %
        # --- Security/Attack Catalysts ---
        elif 'attack' in catalyst.lower() or 'security' in catalyst.lower() or 'hack' in catalyst.lower() or 'exploit' in catalyst.lower():
             catalyst_insights['type'] = 'Security Catalyst'
             catalyst_insights['action'] = 'Pantau insiden keamanan, respon tim, dan dampak terhadap kepercayaan.'
             analysis_result['onchain_signals']['security_incident_score'] = round(random.uniform(0, 100), 2) # Inverse, lower is worse
        # --- General Catalysts ---
        else:
            catalyst_insights['type'] = 'General Catalyst'
            catalyst_insights['action'] = f'Pantau perkembangan umum terkait "{catalyst}".'
            # Assign a general signal if none matched
            analysis_result['onchain_signals']['general_activity'] = round(random.uniform(0, 100), 2)

        analysis_result['catalyst_insights'] = catalyst_insights

        # --- Simulasi Sinyal Tambahan Berdasarkan Lampiran ---
        # --- Derivatives Signals ---
        if 'perp' in category or 'futures' in category or 'options' in category or 'derivatif' in category:
            analysis_result['derivatives_signals']['open_interest'] = round(random.uniform(10000000, 1000000000), 2)
            analysis_result['derivatives_signals']['funding_rate'] = round(random.uniform(-0.1, 0.1), 4)
            analysis_result['derivatives_signals']['basis_rate'] = round(random.uniform(-5, 5), 2) # basis points
            analysis_result['derivatives_signals']['oi_concentration'] = round(random.uniform(0, 100), 2) # %

        # --- Sentiment Signals ---
        # (Sudah diisi berdasarkan katalis, tambahkan simulasi umum)
        if 'sentiment_signals' not in analysis_result or not analysis_result['sentiment_signals']:
             analysis_result['sentiment_signals']['general_sentiment'] = round(random.uniform(-1, 1), 2)
             analysis_result['sentiment_signals']['news_sentiment'] = round(random.uniform(-1, 1), 2)

        # --- Macro & Geopolitical Signals ---
        # (Sudah diisi berdasarkan katalis, tambahkan simulasi umum)
        if 'macro_geopolitical_signals' not in analysis_result or not analysis_result['macro_geopolitical_signals']:
             analysis_result['macro_geopolitical_signals']['macro_risk_score'] = round(random.uniform(0, 100), 2)

        # --- Technical Indicators ---
        # (Sudah diisi berdasarkan kategori, tambahkan simulasi umum)
        if 'technical_indicators' not in analysis_result or not analysis_result['technical_indicators']:
             analysis_result['technical_indicators']['rsi'] = round(random.uniform(30, 70), 2)
             analysis_result['technical_indicators']['macd'] = round(random.uniform(-2, 2), 2)

        # --- Mathematical Analysis ---
        analysis_result['mathematical_analysis']['hurst_exponent'] = round(random.uniform(0.3, 0.8), 2) # <0.5 mean-reverting, >0.5 trending
        analysis_result['mathematical_analysis']['shannon_entropy'] = round(random.uniform(0.5, 2.0), 2) # Measure of disorder
        analysis_result['mathematical_analysis']['lyapunov_exponent'] = round(random.uniform(-0.5, 0.5), 2) # Positive indicates chaos

        # --- Warfare Principles ---
        analysis_result['warfare_principles']['flank_vulnerability'] = round(random.uniform(0, 100), 2) # Lower is better
        analysis_result['warfare_principles']['decoy_position_level'] = round(simulated_price * random.uniform(0.95, 1.05), 2) # Simulated level
        analysis_result['warfare_principles']['supply_line_security'] = round(random.uniform(0, 100), 2) # Exchange API uptime/security proxy

        # --- Futuristic Analysis ---
        analysis_result['futuristic_analysis']['black_swan_probability'] = round(random.uniform(0, 10), 2) # %
        analysis_result['futuristic_analysis']['regime_shift_signal'] = round(random.uniform(0, 100), 2) # Early warning
        analysis_result['futuristic_analysis']['predictive_power_score'] = round(random.uniform(0, 100), 2) # 7-day horizon accuracy proxy

        # --- Key Levels ---
        # Simulasi berdasarkan harga simulasi
        if analysis_result['simulated_market_data'].get('price'):
            base_price = analysis_result['simulated_market_data']['price']
            analysis_result['key_levels']['support_1'] = round(base_price * random.uniform(0.95, 0.98), 4)
            analysis_result['key_levels']['support_2'] = round(base_price * random.uniform(0.90, 0.95), 4)
            analysis_result['key_levels']['resistance_1'] = round(base_price * random.uniform(1.02, 1.05), 4)
            analysis_result['key_levels']['resistance_2'] = round(base_price * random.uniform(1.05, 1.10), 4)
            analysis_result['key_levels']['point_of_control'] = round(base_price * random.uniform(0.99, 1.01), 4) # Simulasi

        # --- Timing Analysis ---
        analysis_result['timing_analysis']['optimal_entry_window'] = f"{random.randint(0, 23):02d}:00-{random.randint(0, 23):02d}:00 UTC" # Simulasi
        analysis_result['timing_analysis']['volatility_profile_peak'] = f"{random.randint(0, 23):02d}:00-{random.randint(0, 23):02d}:00 UTC" # Simulasi

        # --- Risk Management ---
        analysis_result['risk_management']['max_drawdown_risk'] = round(random.uniform(10, 50), 2) # %
        analysis_result['risk_management']['portfolio_beta_to_btc'] = round(random.uniform(0.5, 1.5), 2)
        analysis_result['risk_management']['kelly_criterion_position_size'] = round(random.uniform(0.1, 10), 2) # % of portfolio

        # --- Simulasi Skor Keyakinan (Confidence Score) ---
        priority_score_map = {'Sangat Tinggi': 0.9, 'Tinggi': 0.75, 'Sedang': 0.6, 'Rendah': 0.4, 'Sangat Rendah': 0.2}
        vol_score = priority_score_map.get(volume_level, 0.5)
        # Estimasi kasar untuk katalis score
        cat_first_word = catalyst.split(',')[0].split()[0].lower() if catalyst else 'rendah'
        cat_score = priority_score_map.get(cat_first_word, 0.5)
        analysis_result['confidence_score'] = round((vol_score + cat_score) / 2, 2)

        logging.debug(f"Analisis untuk {symbol} selesai. Confidence Score: {analysis_result['confidence_score']}")
        return analysis_result
# --- CONTOH PENGGUNAAN (Untuk debugging) ---
# --- CONTOH PENGGUNAAN (Untuk debugging) ---
# --- Bagian Sebelum yang Salah ---
if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Mock sederhana untuk orchestrator
    class MockIntelligenceAggregator:
        pass # Tidak digunakan dalam simulasi ini

    class MockPerceptionSystem:
        def __init__(self):
            self.intelligence_aggregator = MockIntelligenceAggregator()

    class MockOrchestrator:
        def __init__(self):
            self.perception_system = MockPerceptionSystem()

    orchestrator = MockOrchestrator()

    # Buat instance scanner
    scanner = CryptoEcosystemScanner(orchestrator)

    # Snapshot persepsi dummy
    dummy_perception = {"market_sentiment": "neutral", "fear_greed_index": 50}

    # Jalankan pemindaian untuk beberapa koin teratas (misalnya 5)
    print("Memulai pemindaian ekosistem...")
    # --- Bagian yang Salah ---
    # results = scanner.scan_all_ecosystem(dummy_perception, top_n=20)
    # --- Perbaikan ---
    results = scanner.scan_top_coins(dummy_perception, top_n=20)
    # --- Bagian Sesudah yang Salah ---

    # Cek hasil
    print(f"\n--- Hasil Pemindaian ({len(results)} koin) ---")
    for result in results:
        if 'error' in result:
            print(f"ERROR untuk {result['coin_info']['simbol']}: {result['error']}")
        else:
            symbol = result['coin_info']['simbol']
            name = result['coin_info']['nama_lengkap']
            category = result['coin_info']['kategori']
            catalyst = result['coin_info']['potensi_katalis']
            confidence = result['confidence_score']
            price = result['simulated_market_data'].get('price', 'N/A')
            print(f"\nKoin: {symbol} ({name})")
            print(f"  Kategori: {category}")
            print(f"  Katalis: {catalyst}")
            print(f"  Harga Simulasi: ${price}")
            print(f"  Skor Keyakinan: {confidence}")
            print(f"  Wawasan Kategori (fokus): {result['category_insights'].get('focus', 'N/A')}")
            print(f"  Wawasan Katalis (tipe): {result['catalyst_insights'].get('type', 'N/A')}")
            # Cek apakah berbagai jenis sinyal telah diisi
            print(f"  Sinyal On-Chain Diisi: {bool(result['onchain_signals'])}")
            print(f"  Sinyal Sentimen Diisi: {bool(result['sentiment_signals'])}")
            print(f"  Level Kunci Diisi: {bool(result['key_levels'])}")
            # Tambahkan pemeriksaan lain sesuai kebutuhan

    print("\ncrypto_ecosystem_scanner.py vFinal siap untuk diintegrasikan.")
