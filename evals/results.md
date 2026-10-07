Retriever: bm25, 36 chunks, 33 questions

- hit@3 (file): 27/28 = 96%
- hit@3 (chunk): 26/28 = 93%
- refusal accuracy (out of scope): 4/5 = 80%
- false refusals (in scope): 1/28

pass = expected chunk in the top 3, or correctly refused.

| pass | question | expected | top-3 retrieved |
|---|---|---|---|
| yes | Who do I contact about course reserves in Leganto? | contacts_help_services.md / Course reserves, Leganto, Pay-Per-Use | contacts_help_services.md / Course reserves, Leganto, Pay-Per-Use |
| yes | OneSearch isn't returning the right results, who should I tell? | contacts_help_services.md / OneSearch Functionality | contacts_help_services.md / OneSearch Functionality |
| NO | Who handles interlibrary loan requests? | contacts_help_services.md / ILL, Rapido (CSU+) | sjsu_parking_permit_request.md / SJSU Parking Permit Request; event_funding_request.md / Event Funding Request Form; contacts_help_services.md / Acquisitions - Serials holdings, Streaming Media requests |
| yes | My office computer won't start, how do I reach desktop support? | contacts_help_services.md / Desktop Support - IT Crowd | contacts_help_services.md / Desktop Support - IT Crowd; org_chart_sjsu_king_library.md / Dean’s Office |
| yes | Who manages the KLEVR Lab? | contacts_help_services.md / KLEVR Lab | contacts_help_services.md / KLEVR Lab; contacts_help_services.md / Materials Lab; contacts_help_services.md / Rapid Prototype Lab |
| yes | Who can help me deposit my thesis in ScholarWorks? | contacts_help_services.md / Institutional Repository - ScholarWorks | contacts_help_services.md / Institutional Repository - ScholarWorks |
| yes | Who do I email about setting up an eBook trial? | contacts_help_services.md / Electronic Resources - eBooks, trials | contacts_help_services.md / Electronic Resources - eBooks, trials |
| NO | Who is in charge of the library website? | contacts_help_services.md / Web Team | (refused) |
| yes | Who do I ask about using the microfilm machines? | contacts_help_services.md / Microfilm Machines | contacts_help_services.md / Microfilm Machines |
| yes | Who sets up AV equipment in library classrooms? | contacts_help_services.md / Media Services, Classrooms, AV Setups | contacts_help_services.md / Media Services, Classrooms, AV Setups |
| yes | I need an Alma Analytics report, who builds those? | contacts_help_services.md / Alma Analytics - reports, dashboards | contacts_help_services.md / Alma Analytics - reports, dashboards; contacts_help_services.md / Alma functionality, config, troubleshooting |
| yes | Who handles cataloging and metadata? | contacts_help_services.md / Metadata - Cataloging | contacts_help_services.md / Metadata - Cataloging |
| yes | Who manages LibAnswers and LibChat? | contacts_help_services.md / LibApps (LibAnswers, LibChat, etc.) | contacts_help_services.md / LibApps (LibAnswers, LibChat, etc.) |
| yes | Who is the contact for the library chatbot? | contacts_help_services.md / Chatbot | contacts_help_services.md / Chatbot |
| yes | Who handles streaming media requests? | contacts_help_services.md / Acquisitions - Serials holdings, Streaming Media requests | contacts_help_services.md / Acquisitions - Serials holdings, Streaming Media requests; sjsu_parking_permit_request.md / SJSU Parking Permit Request; event_funding_request.md / Event Funding Request Form |
| yes | A student's library account is blocked, who manages patron accounts? | contacts_help_services.md / Patron account management | contacts_help_services.md / Patron account management; contacts_help_services.md / Student Computing Services (SCS); org_chart_sjsu_king_library.md / Associate Deans |
| yes | Who do I talk to about government publications? | contacts_help_services.md / Government Publications | contacts_help_services.md / Government Publications |
| yes | Who runs the Technology Training Center? | contacts_help_services.md / Technology Training Center (TTC) | contacts_help_services.md / Technology Training Center (TTC) |
| yes | Who handles visiting scholars and instructional affiliates? | contacts_help_services.md / Visiting Scholars, Instructional Affiliates | contacts_help_services.md / Visiting Scholars, Instructional Affiliates |
| yes | Who is responsible for the library's digital collections? | contacts_help_services.md / Digital Collections | contacts_help_services.md / Digital Collections; contacts_help_services.md / Chatbot; contacts_help_services.md / Library Data Dashboard |
| yes | Who is the dean of the King Library? | org_chart_sjsu_king_library.md / Dean’s Office | org_chart_sjsu_king_library.md / Dean’s Office; org_chart_sjsu_king_library.md / Associate Deans |
| yes | Who is the executive assistant to the dean? | org_chart_sjsu_king_library.md / Dean’s Office | org_chart_sjsu_king_library.md / Dean’s Office; org_chart_sjsu_king_library.md / Associate Deans; org_chart_sjsu_king_library.md / Faculty Librarians |
| yes | Who is the associate dean for innovation and resource management? | org_chart_sjsu_king_library.md / Associate Deans | org_chart_sjsu_king_library.md / Associate Deans; org_chart_sjsu_king_library.md / Dean’s Office; org_chart_sjsu_king_library.md / Faculty Librarians |
| yes | Who is the head of acquisitions? | org_chart_sjsu_king_library.md / Resource Management & Delivery | org_chart_sjsu_king_library.md / Resource Management & Delivery; contacts_help_services.md / Acquisitions - Funds, Vendors; contacts_help_services.md / Acquisitions - Purchasing, Licensing |
| yes | Who is the library's director of development? | org_chart_sjsu_king_library.md / Dean’s Office | org_chart_sjsu_king_library.md / Dean’s Office; org_chart_sjsu_king_library.md / Resource Management & Delivery |
| yes | Which faculty librarians work at the King Library? | org_chart_sjsu_king_library.md / Faculty Librarians | org_chart_sjsu_king_library.md / Faculty Librarians; org_chart_sjsu_king_library.md / Associate Deans |
| yes | How do I request a parking permit for a guest? | sjsu_parking_permit_request.md / SJSU Parking Permit Request | sjsu_parking_permit_request.md / SJSU Parking Permit Request; event_funding_request.md / Event Funding Request Form; contacts_help_services.md / Acquisitions - Serials holdings, Streaming Media requests |
| yes | How do I request funding for a library event? | event_funding_request.md / Event Funding Request Form | event_funding_request.md / Event Funding Request Form; sjsu_parking_permit_request.md / SJSU Parking Permit Request; contacts_help_services.md / Acquisitions - Serials holdings, Streaming Media requests |
| yes | What are the library hours during finals week? | (refuse) | (refused) |
| yes | How much is the fine for an overdue book? | (refuse) | (refused) |
| NO | Can I reserve a group study room? | (refuse) | contacts_help_services.md / Course reserves, Leganto, Pay-Per-Use; contacts_help_services.md / Web Team; contacts_help_services.md / Desktop Support - IT Crowd |
| yes | How do I print from my laptop in the library? | (refuse) | (refused) |
| yes | When is the SJSU tuition payment deadline? | (refuse) | (refused) |
