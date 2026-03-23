#!/usr/bin/env python3
"""
Add Load Board Sources to Database
"""
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Load board sources to add
LOAD_SOURCES = [
    {
        "name": "Logistware",
        "website": "https://www.logistware.ca",
        "email": "customerservice@logistware.ca",
        "description": "Canada load board where shippers book faster and carriers win more bids. Verified Canadian loads with SHA recognition.",
        "type": "load_board",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Multi Action",
        "website": "https://www.multiaction.ca",
        "email": "jfortin@multiaction.ca",
        "phone": "(418) 660-1180, poste 237",
        "description": "Shipping Department - Multi Action. Hours: 7AM to 4PM (Closed 12-1PM). Address: 6890 boulevard Ste-Anne, L'Ange-Gardien, QC G0A 2K0 Canada",
        "type": "shipping_partner",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "UShip Canada",
        "website": "https://www.uship.com/ca/",
        "email": None,
        "description": "UShip Canada - Online marketplace for shipping and logistics services.",
        "type": "load_board",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "DAT Load Board",
        "website": "https://www.dat.com/find-truck-loads",
        "email": None,
        "description": "DAT - Find truck loads and manage your trucking business. Largest load board with real-time freight matching.",
        "type": "load_board",
        "country": "North America",
        "verified": True,
    },
    {
        "name": "PickATruckLoad",
        "website": "https://www.pickatruckload.com",
        "email": None,
        "description": "Load board source for freight and shipping opportunities.",
        "type": "load_board",
        "country": "North America",
        "verified": True,
    },
    {
        "name": "Freightera",
        "website": "https://www.freightera.com",
        "email": "clientcare@freightera.com",
        "phone": "(800) 886-4870",
        "description": "Canadian freight and logistics marketplace. Hours: 5:30 AM – 5:00 PM PST Mon-Fri. Office: 408 – 55 Water Street, Vancouver, BC V6B 1A1, Canada. Accounting: Ext. 4",
        "type": "load_board",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Warehouse Discovery",
        "website": "https://warehousediscovery.com/",
        "email": None,
        "description": "Warehouse Services Directory (Canada) - Contract & fulfillment warehouses, refrigerated storage, 3PL providers.",
        "type": "warehouse_directory",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "CIREA - Warehouse Locator",
        "website": "https://www.cirea.ca/warehouse-locator",
        "email": "info@cirea.ca",
        "description": "Canadian Industrial Real Estate Affiliation warehouse locator. Find general warehouses, refrigerated storage, co-packing, fulfillment & 3PL in major cities (Vancouver, Toronto, Montreal, Calgary).",
        "type": "warehouse_directory",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Scott's Directories - Warehouse & 3PL",
        "website": "https://www.scottsdirectories.com/list-of-warehouse-companies-in-canada/",
        "email": None,
        "description": "Directory of thousands of logistics, 3PL, and warehouse companies in Canada with contact data, industry, locations, storage services, and transportation options.",
        "type": "directory",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "GoodFirms - Warehousing Companies Canada",
        "website": "https://www.goodfirms.co/supply-chain-logistics-companies/warehousing/canada",
        "email": None,
        "description": "List of top-rated warehousing and fulfillment companies in Canada (2026) with detailed reviews and ratings.",
        "type": "directory",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "VersaCold",
        "website": "https://www.foodlogistics.com/warehousing/cold-storage/company/21578449/versacold",
        "email": "mmayer@iron.markets",
        "phone": "647-296-5014",
        "description": "Largest temperature-sensitive warehouse network in Canada. Provider of refrigerated storage and cold chain logistics. Contact: Marina Mayer (mmayer@iron.markets), Brian Hines (bhines@iron.markets), Susan Joyce (sjoyce@iron.markets)",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Congebec Logistics",
        "website": "https://congebec.com/en/",
        "email": None,
        "phone": "1 877 683-3491",
        "description": "Storage, distribution, and cold transport services. Multi-temperature warehouse and logistics provider in Canada. Head Office: 810, avenue Godin, Québec, QC G1M 2X9. Phone: 418 683-3491, Fax: 418 683-6387",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "DelGate",
        "website": "https://delgate.ca",
        "email": "rates@delgate.ca",
        "phone": "+1 833-335-4283",
        "description": "3PL and distribution company offering warehouses and shipping services in Canada. Located at Unit1 - 403 East Kent Ave North, Vancouver BC. Sales: rates@delgate.ca, Order Help: help@delgate.ca, Alt Phone: 778-340-1111",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "MTS Logistics",
        "website": "https://mtslogistics.com",
        "email": "info@mtslogistics.com",
        "description": "Canadian logistics and transportation services provider.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Canadian Freightways",
        "website": "https://canadianfreightways.com",
        "email": "info@canadianfreightways.com",
        "description": "Canadian freight transportation and logistics company.",
        "type": "freight_carrier",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Trans Logistics",
        "website": "https://translogistics.com",
        "email": "info@translogistics.com",
        "description": "Transportation and logistics services provider in Canada.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Cascades",
        "website": "https://www.cascades.com",
        "email": "info@cascades.com",
        "description": "Canadian packaging and logistics solutions provider.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Supply Chain Canada",
        "website": "https://www.supplychaincanada.com",
        "email": "info@supplychaincanada.com",
        "description": "Supply chain management and logistics services in Canada.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "WCP Logistics",
        "website": "https://wcplogistics.com",
        "email": "info@wcplogistics.com",
        "description": "Warehouse and logistics services provider in Canada.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "GoBolt",
        "website": "https://gobolt.com",
        "email": "info@gobolt.com",
        "description": "3PL and Warehousing solutions provider in Canada.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Lynden Logistics",
        "website": "https://lynden.com",
        "email": "info@lynden.com",
        "description": "Professional 3PL and warehousing services throughout Canada and North America.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Montreal Go Transport",
        "website": "https://gotransport.ca",
        "email": "info@gotransport.ca",
        "description": "3PL logistics and transportation services in Montreal and Quebec region.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Bulletproof Logistics",
        "website": "https://bulletprooflogistics.com",
        "email": "info@bulletprooflogistics.com",
        "description": "3PL warehouse and logistics solutions provider in Canada.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Approved Cold Storage",
        "website": "https://approvedcoldstorage.com",
        "email": "info@approvedcoldstorage.com",
        "description": "Cold storage and refrigerated warehousing services in Toronto area.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "RecordXpress",
        "website": "https://recordxpress.com",
        "email": "info@recordxpress.com",
        "description": "Warehousing and document storage services based in Richmond.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Portside Warehousing and Distribution",
        "website": "https://portsidewarehousing.com",
        "email": "info@portsidewarehousing.com",
        "description": "Warehousing and distribution services in Mississauga, Ontario.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Newell's Express Worldwide Logistics",
        "website": "https://newellsexpress.com",
        "email": "info@newellsexpress.com",
        "description": "3PL and logistics services based in Oakville, Ontario.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Pak Mail Canada",
        "website": "https://pakmailcanada.com",
        "email": "info@pakmailcanada.com",
        "description": "3PL packaging and shipping services in Mississauga.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Tern Worldwide Limited",
        "website": "https://ternworldwide.com",
        "email": "info@ternworldwide.com",
        "description": "International 3PL and logistics provider based in Etobicoke.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "XTL Inc",
        "website": "https://xtl.com",
        "email": "info@xtl.com",
        "description": "3PL transportation and logistics services in Brantford, Ontario.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Tenaxx Logistics",
        "website": "https://tenaxxlogistics.com",
        "email": "info@tenaxxlogistics.com",
        "description": "3PL warehouse and logistics solutions in Ottawa.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "ByExpress",
        "website": "https://byexpress.com",
        "email": "info@byexpress.com",
        "description": "Warehousing and distribution services based in Richmond.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Cargo Dynamics Logistics",
        "website": "https://cargodynamicslogistics.com",
        "email": "info@cargodynamicslogistics.com",
        "description": "Warehousing and logistics services in Guelph, Ontario.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Lane Logistics",
        "website": "https://lanelogistics.com",
        "email": "info@lanelogistics.com",
        "description": "3PL Ontario warehousing and distribution based in Mississauga.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "ADLI Logistics",
        "website": "https://adlilogistics.com",
        "email": "info@adlilogistics.com",
        "description": "3PL warehouse and logistics provider in Port Coquitlam, BC.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Liberate Logistics",
        "website": "https://liberatelogistics.com",
        "email": "info@liberatelogistics.com",
        "description": "3PL and logistics solutions based in Oakville, Ontario.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Olivan Integrated Marketing",
        "website": "https://olivanintegratedmarketing.com",
        "email": "info@olivanintegratedmarketing.com",
        "description": "3PL and integrated logistics services in Brampton, Ontario.",
        "type": "logistics_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "GBT Logistics & Packaging Inc",
        "website": "https://gbtlogistics.com",
        "email": "info@gbtlogistics.com",
        "description": "Warehousing and packaging logistics services in Etobicoke.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Ship Apollo",
        "website": "https://shipapollo.com",
        "email": "info@shipapollo.com",
        "description": "Fulfillment centre and warehousing services based in Delta, BC.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Evolution Fulfillment",
        "website": "https://evolutionfulfillment.com",
        "email": "info@evolutionfulfillment.com",
        "description": "E-commerce fulfillment and warehouse services in Laval, Quebec.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Fredyma International Inc",
        "website": "https://fredyma.com",
        "email": "info@fredyma.com",
        "description": "Warehousing and international logistics services in Toronto.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Enterprise Ecom Logistics",
        "website": "https://enterpriseecomlogistics.com",
        "email": "info@enterpriseecomlogistics.com",
        "description": "E-commerce focused 3PL and warehousing solutions.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "Northland Fulfillment",
        "website": "https://northlandfulfillment.com",
        "email": "info@northlandfulfillment.com",
        "description": "Fulfillment and warehouse services provider in Canada.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "18 Wheels Warehousing and Trucking",
        "website": "https://18wheelslogistics.com",
        "email": "info@18wheelslogistics.com",
        "description": "Warehousing and transportation services provider in Canada.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "ShipTop",
        "website": "https://shiptop.com",
        "email": "info@shiptop.com",
        "description": "Warehousing and fulfillment services for e-commerce businesses.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
    {
        "name": "SHIPHYPE Fulfillment",
        "website": "https://shiphype.com",
        "email": "info@shiphype.com",
        "description": "Advanced fulfillment and logistics services for online retailers.",
        "type": "warehouse_provider",
        "country": "Canada",
        "verified": True,
    },
]

async def add_load_sources():
    db_url = os.getenv('ASYNC_DATABASE_URL').replace('?sslmode=require', '')
    engine = create_async_engine(db_url, echo=False, connect_args={'ssl': True})
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("📊 Adding load sources to database...\n")
            
            for source in LOAD_SOURCES:
                # Check if source already exists
                result = await session.execute(
                    text("SELECT id FROM carriers WHERE email = :email"),
                    {"email": source["email"]}
                )
                existing = result.scalar()
                
                if existing:
                    print(f"⏭️  {source['name']} already exists (ID: {existing})")
                    continue
                
                # Add new source
                insert_query = text("""
                    INSERT INTO carriers (name, email, phone, is_active, created_at, tenant_id)
                    VALUES (:name, :email, :phone, :is_active, :created_at, :tenant_id)
                    RETURNING id
                """)
                
                result = await session.execute(insert_query, {
                    "name": source["name"],
                    "email": source["email"],
                    "phone": None,  # Can be added later
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "tenant_id": None,
                })
                
                new_id = result.scalar()
                print(f"✅ {source['name']}")
                print(f"   📧 Email: {source['email']}")
                print(f"   🌐 Website: {source['website']}")
                print(f"   📝 Description: {source['description']}")
                print(f"   🆔 ID: {new_id}")
                print()
            
            await session.commit()
            print("✅ All sources saved successfully!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_load_sources())
