# CSC289 Programming Capstone
# Project Plan 


### Project Name: Novel Solutions
### Team Number:  9
### Team project Manager : Timothy Hayes
---

### Team Member Details

| Name    | Email    | Role    |
| ------ | ------ | ----- |
| Timothy Hayes | trhayes@my.waketech.edu | Project Manager |
| Jake Medlock | jsmedlock@my.waktech.edu | Team Member |
| Safia Koech | sckoech@my.waketech.edu	| Team Member | 
| Hayat Outghate | houtghate@my.waketech.edu | Team Member |
| Nicholas Pacejka | nepacejka@my.waketech.edu | Team Member |
| Andres Jaramillo | afjaramillo@my.waketech.edu	| Team Member |
| Andrew Weller |	ajweller@my.waketech.edu | Team Member | 
| Seth VanDuinen | arvanduinen@my.waketech.edu | Team Member | 

---

### Project Goal - Timothy
--- 
Our goal is to create a POS and inventory management system that streamlines bookstore operations and boosts efficiency. Using Agile and SCRUM methodologies, the team will ensure that every project phase delivers key features that meet user requirements and align with business objectives.

### Project Objectives - Timothy
---
- Develop a system to handle POS functions, manage bookstore inventory, allowing users to easily create, modify, delete, and restore items, ensuring accurate and up-to-date stock records.

- Build a point-of-sale (POS) system that facilitates seamless transactions, including cart management, payment processing, returns/refunds, and updates to inventory in real-time.

- Enable simultaneous usage of the system by multiple cashiers and managers, allowing for smooth operations in a busy retail environment.

- Provide tools for staff and managers to generate detailed and customizable reports on sales trends and inventory status to inform decision-making.


### Project Scope - Andrew
---
**A Novel Solution** aims to provide a **comprehensive and efficient system** for managing **bookstore inventory and point-of-sale (POS) operations**, streamlining both sales transactions and stock management. The system will support essential bookstore functions, ensuring ease of use for staff and business owners while maintaining security, reliability, and scalability.

#### 1.	**Included Features (In-Scope):**
The following features and functionalities are within the scope of this project:

- **Inventory Management:**

	- Adding, updating, deleting, and restoring book inventory and batches.

	- Categorization by genre, author, and format (e.g., paperback, hardcover).

	- Barcode scanning for quick stock-taking and updates.

	- Low-stock alerts and automated reordering suggestions.


- **Point-of-Sale (POS) System:**

	- Quick and efficient checkout process with barcode scanning.

	- Cart management: adding/removing items, applying discounts, and calculating totals.

	- Support for multiple payment methods, including **cash, credit/debit cards, and mobile payments.**

	- Handling returns and refunds, including inventory updates and transaction lookups.

	- Receipt generation (print and email options).

	- Multi-user support for **cashiers, managers, and administrators**.

- **Reporting & Analytics:**

	- Generating daily, weekly, and custom sales reports.

	- Inventory turnover tracking and trend analysis.

	- Exporting reports for business insights and decision-making.

- **Security & Access Control:**

	- Role-based access control (cashiers, managers, and administrators).

	- Password encryption and salting for secure user authentication.

	- Automated backup and redundancy services to prevent data loss.

	- Secure payment processing compliant with **industry standards** (PCI DSS).

- **System Infrastructure & Support:**

	- Server-client model hosted on a **local bookstore server** for control over operations.

	- Multi-device accessibility (desktop-based system with support for POS terminals).

	- Offline functionality for core POS and inventory features, with cloud synchronization when online.

#### 2. **Excluded Features (Out-of-Scope):**
The following features are explicitly excluded from the current project scope to maintain focus and feasibility:

- **Mobile Application** – No mobile version of the software will be developed at this stage.
- **Complex Payment Integrations** – Advanced third-party payment systems (e.g., cryptocurrency, buy-now-pay-later services) are not supported.
- **Biometric Security** – No implementation of fingerprint or facial recognition for authentication.

- **E-Commerce Functionality** – The system will not support online book sales or customer-facing web stores.
- **Advertising & Monetization** – No integration of in-system advertisements or paid promotions.


#### 3. **Future Considerations:**
While the current version focuses on physical bookstore management, future iterations may explore:
- Integration with HR systems (employee scheduling, payroll tracking).
- Loyalty programs (reward points, customer accounts).
- E-commerce expansion (API for online book sales).
- Multi-store support (centralized inventory for bookstore chains).


### Project Assumptions - Seth
---
For all bookstores that will utilize A Novel Solution systems, it can be reasonably assumed that:
- All locations will employ staff with basic technical knowledge of POS systems, thereby allowing development to operate based on a set of common knowledge. 
- All locations will systematize sales processing and inventory management via the use of barcode scanners rather than entering information such as ISBNs manually. 
- All locations will process credit card transactions and receive access to external servers through maintained internet access. 


### Project Constraints - Hayat
---
Project constraints are requirements or limitations that define the boundaries within which the system must operate. Managing these constraints is essential to ensure successful planning, execution, and completion of the project.

- **Time Constraints:**
The project must be completed within a specific timeframe, limiting the duration available for planning, developing, testing, and deployment.
 
- **Cost Constraints:** 
	- Budget Limitation: The project must be completed within a defined budget. This would limit the resources that can be allocated to hardware, development, testing, and other related activities.
	- Resources Allocation: The project should be developed with the available human resources, considering the budgetary constraints.
 
- **Scoop Constraints:** 
The initial phase of the project will focus only on essential and specific functionalities, such as POS integration, inventory management, and financial reporting. Additional features may not be included in this first phase; however, they can be considered for future phases.
 
- **Quality Constraints:**
	- Performance Standards: The system must meet specific performance benchmarks, such as fast transaction processing times and updates, which must be processed within a certain timeframe. 
	- User Experience: The system should be user-friendly, intuitive, and easy to use, minimizing training for bookstore staff and ensuring customers have smooth transaction experience.
 
- **Resource Constraints:**
	- Hardware Requirements: The system must be compatible with specific hardware such as barcode scanners, receipt printer, which restricts hardware options and leads to increase the costs.
	- Internet Connectivity: The system requires reliable internet access for real-time updates, which may limit the project’s deployment in areas with unreliable networks.
 
- **Legal and Regulatory Constraints:** 
	- Data Protection Compliance: The system must adhere to local and international data protection laws, such as GDPR, CCPA, which can affect data architecture and storage options.
	- Payment processing Regulations: The integration with payment gateways such as Stripe, PayPal, and Square must meet with their respective legal and security standards.
 
- **Integration Constraints:** 
	- Payment Gateway Compatibility: The system must support integration with widely reliable payment platforms, such as Stripe, PayPal, and Square, offering customers various payment options (credit card, debit card, and other online payment options) and ensuring a seamless transaction experience.
	- Hardware and API Integration: Utilization of barcode scanning devices and integration of third-party APIs impose technical requirements on both hardware and software sides of the project. Thus, it requires work with technical teams, developers, and third-party service providers to ensure smooth communication between devices, APIs, and the software.
	- Accounting Software Integration: The system must be compatible with accounting software, such as QuickBooks, to ensure real-time financial reporting and management.
 
- **Technical Constraints:**
	- Scalability: The system should be able to scale to accommodate increasing numbers of users, transactions, and locations without requiring significant architectural changes.
	- Platform compatibility: The system must be compatible with widely used operating systems such as Windows and macOS.  


### Project Resources Required - Safia 
---
The personnel required for this project are a Test Manager, Test Engineers, Developers, and a Test automation Engineer.
 
- **Test Manager:** – Oversees scheduling, test execution, and
reporting.
- **Test Engineers:** – Responsible for manual and automated test execution.
- **Developers:** – Responsible for developing and fixing identified bugs.
- **Test Automation Engineer:** – Develop and maintain test scripts.
 
The materials required for the success of this project are:
 
- **Project scope:** A clearly defined outline of the boundaries is necessary to prevent scope creep.
- **Deliverables:** Details the results the project needs to generate at each stage,
- **Stakeholders:** A single person or multiple people that are interested in the project's success (customers, developers, executives, etc.)
- **Communication Plan:** Effective communication methods to keep the stakeholders updated.
- **Project Objectives:** Clearly defined goals and results of the project.
- **Risk Management Plan:** Outlines potential risks, evaluates the projected impact, offers potential mitigation tactics.
- **Project Schedule:** A period that outlines important milestones, task reliance, and deadlines.
 
The tools required for this project are:
 
**Trello:** Used for planning, team collaboration, and organization.
 
**GitHub:** Used for code storage, version control, collaboration, and continuous integration.
 
**Microsoft Teams:** Used for communication and virtual meetings between team members.


### Team Collaboration and Communication – Jake 
---
**Microsoft Teams:**

Microsoft teams will be the main communication platform for this project.
- 	Teams as a whole will be used to schedule meetings and to keep each other informed throughout the project lifecycle.
-	Chat features will be used to ensure each team member is sharing ideas, questions, and contribute assistance to other members. 
-	Teams’ meetings will be used to hold 2 meetings per week.

**GitHub:**
-	will be used as version control to ensure stability of each build and to easily revert to older versions if needed.
-	will be used to manage code reviews: each push to the repository will require code reviews by at multiples members to ensure code is evaluated before being pushed into the codebase. 
-	will be used to track team member contributions allowing ease of access to what each team member has contributed, who has revised, edited or worked on each piece of code within the codebase. 
Each team member will easily be able to contribute to the project with the use of GitHub.

**Email:**
-	will be used to contact team members if they are unreachable by teams.
-	will be used for weekly updates and to assure team members have received schedule meeting invitations

**Project Management Collaboration:**

**Communication Plan:**

- **Weekly Team Meetings:**
	- Team Members are required to attend at least one meeting each week
    - There will be a meeting each week on Tuesday from 6:30 p.m. - 7:00 p.m.
    - An additional meeting will be held each week on Thursday from 7:00p.m - 7: 30p.m


- **Daily Team Communication:**
    -	The group will collaborate daily to ensure each team member can share questions, concerns, and ideas.
    -	Team chat will be open for any member to update the team on their progress and inform the team if they will be unable to work on the project for an extended period.
    -	Group members will be able to reach out within Teams chat to for help or to jump in a call if another team member would like to help come together to pair program.

- **End of week update:**
    -	Each member will be required to update the team at least 2 days before due dates to allow other team members to jump in and help if needed.


### Project Documentation - Nicholas Pacejka
---
**GitHub:**
-	Used for source code version control
-	Managing and sharing code
-	Reporting bugs
-	Keeping track of contributions made by each individual team member.

**Microsoft Teams:**
-	Main communication tool
-	Meeting notes will be shared and stored in Teams
-	Small project documents kept in Group files

**Trello:**
-	Main project management tool
-	Organize and prioritize project assignments
-	Plan assignments and track progress through project boards and task lists
-	Set due dates


### Project Management Plan and Methodologies - Andres / Jake (backup)
---
Our Project Management plan follows Agile practices and utilizes the SCRUM Framework.
These practices will allow us to perform iterative development, continuous feedback, with rapid delivery and the ability to quickly adapt to change.


**Project Management Practices:**

**Sprint Planning:**
-	Each sprint is planned on the project schedule along with its tasks and assignments to team members.
-	This project schedule is updated weekly, Sprints vary from 2 to 4 weeks.
-	Each sprint goal is to quickly develop fully functional features for inventory management, inventory management and Point of Sale support.

**Daily Messages:**
-	The team has an open chat room available daily for team members to discuss issues, concerns, and questions.
-	This allows the team to quickly address issues and keep the team working toward each sprint goal.

**Project Management Tools:**
- **Trello:** used as a project management task tracking board
- **GitHub:** used for version control and CI/CD
- **Microsoft** Teams: used for team communication and meetings
