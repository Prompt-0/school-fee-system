BEGIN TRANSACTION;
CREATE TABLE audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        action TEXT NOT NULL,
        actor TEXT NOT NULL,
        details_json TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
INSERT INTO "audit_logs" VALUES(1,'INVOICE','INV-2026-0001','CREATE','System','{"student_id": "ADM-2026-001", "amount": "22900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(2,'INVOICE','INV-2026-0002','CREATE','System','{"student_id": "ADM-2026-002", "amount": "22400.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(3,'INVOICE','INV-2026-0003','CREATE','System','{"student_id": "ADM-2026-003", "amount": "43900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(4,'INVOICE','INV-2026-0004','CREATE','System','{"student_id": "ADM-2026-004", "amount": "20900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(5,'INVOICE','INV-2026-0005','CREATE','System','{"student_id": "ADM-2026-005", "amount": "25900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(6,'INVOICE','INV-2026-0006','CREATE','System','{"student_id": "ADM-2026-006", "amount": "19900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(7,'INVOICE','INV-2026-0007','CREATE','System','{"student_id": "ADM-2026-007", "amount": "22400.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(8,'INVOICE','INV-2026-0008','CREATE','System','{"student_id": "ADM-2026-008", "amount": "25900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(9,'INVOICE','INV-2026-0009','CREATE','System','{"student_id": "ADM-2026-009", "amount": "16400.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(10,'INVOICE','INV-2026-0010','CREATE','System','{"student_id": "ADM-2026-010", "amount": "25900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(11,'INVOICE','INV-2026-0011','CREATE','System','{"student_id": "ADM-2026-011", "amount": "40400.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(12,'INVOICE','INV-2026-0012','CREATE','System','{"student_id": "ADM-2026-012", "amount": "22900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(13,'INVOICE','INV-2026-0013','CREATE','System','{"student_id": "ADM-2026-013", "amount": "25900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(14,'INVOICE','INV-2026-0014','CREATE','System','{"student_id": "ADM-2026-014", "amount": "20900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(15,'INVOICE','INV-2026-0015','CREATE','System','{"student_id": "ADM-2026-015", "amount": "25900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(16,'INVOICE','INV-2026-0016','CREATE','System','{"student_id": "ADM-2026-016", "amount": "22400.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(17,'INVOICE','INV-2026-0017','CREATE','System','{"student_id": "ADM-2026-017", "amount": "40300.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(18,'INVOICE','INV-2026-0018','CREATE','System','{"student_id": "ADM-2026-018", "amount": "10400.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(19,'INVOICE','INV-2026-0019','CREATE','System','{"student_id": "ADM-2026-019", "amount": "25900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(20,'INVOICE','INV-2026-0020','CREATE','System','{"student_id": "ADM-2026-020", "amount": "22400.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(21,'INVOICE','INV-2026-0021','CREATE','System','{"student_id": "ADM-2026-021", "amount": "25900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(22,'INVOICE','INV-2026-0022','CREATE','System','{"student_id": "ADM-2026-022", "amount": "24500.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(23,'INVOICE','INV-2026-0023','CREATE','System','{"student_id": "ADM-2026-023", "amount": "28000.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(24,'INVOICE','INV-2026-0024','CREATE','System','{"student_id": "ADM-2026-024", "amount": "52000.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(25,'INVOICE','INV-2026-0025','CREATE','System','{"student_id": "ADM-2026-025", "amount": "32000.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(26,'INVOICE','INV-2026-0026','CREATE','System','{"student_id": "ADM-2026-026", "amount": "20500.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(27,'INVOICE','INV-2026-0027','CREATE','System','{"student_id": "ADM-2026-027", "amount": "32000.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(28,'INVOICE','INV-2026-0028','CREATE','System','{"student_id": "ADM-2026-028", "amount": "28000.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(29,'INVOICE','INV-2026-0029','CREATE','System','{"student_id": "ADM-2026-029", "amount": "32000.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(30,'INVOICE','INV-2026-0030','CREATE','System','{"student_id": "ADM-2026-030", "amount": "24250.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(31,'INVOICE','INV-2026-0031','CREATE','System','{"student_id": "ADM-2026-031", "amount": "32000.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(32,'INVOICE','INV-2026-0032','CREATE','System','{"student_id": "ADM-2026-032", "amount": "52000.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(33,'INVOICE','INV-2026-0033','CREATE','System','{"student_id": "ADM-2026-033", "amount": "16900.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(34,'INVOICE','INV-2026-0034','CREATE','System','{"student_id": "ADM-2026-034", "amount": "15400.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(35,'INVOICE','INV-2026-0035','CREATE','System','{"student_id": "ADM-2026-035", "amount": "18400.00"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(36,'PAYMENT','PAY-2026-0001','COLLECT','Sunita Verma','{"amount": "15000.00", "invoice": "INV-2026-0001", "receipt": "REC-2026-0001"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(37,'PAYMENT','PAY-2026-0002','COLLECT','Accounts Office','{"amount": "22400.00", "invoice": "INV-2026-0002", "receipt": "REC-2026-0002"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(38,'PAYMENT','PAY-2026-0003','COLLECT','Rajesh Sharma','{"amount": "20000.00", "invoice": "INV-2026-0003", "receipt": "REC-2026-0003"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(39,'PAYMENT','PAY-2026-0004','COLLECT','Sunita Verma','{"amount": "25900.00", "invoice": "INV-2026-0005", "receipt": "REC-2026-0004"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(40,'PAYMENT','PAY-2026-0005','COLLECT','Counter Cashier','{"amount": "19900.00", "invoice": "INV-2026-0006", "receipt": "REC-2026-0005"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(41,'PAYMENT','PAY-2026-0006','COLLECT','Counter Cashier','{"amount": "12000.00", "invoice": "INV-2026-0008", "receipt": "REC-2026-0006"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(42,'PAYMENT','PAY-2026-0007','COLLECT','Sunita Verma','{"amount": "25900.00", "invoice": "INV-2026-0010", "receipt": "REC-2026-0007"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(43,'PAYMENT','PAY-2026-0008','COLLECT','Accounts Office','{"amount": "10000.00", "invoice": "INV-2026-0012", "receipt": "REC-2026-0008"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(44,'PAYMENT','PAY-2026-0009','COLLECT','Counter Cashier','{"amount": "25900.00", "invoice": "INV-2026-0013", "receipt": "REC-2026-0009"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(45,'PAYMENT','PAY-2026-0010','COLLECT','Sunita Verma','{"amount": "8000.00", "invoice": "INV-2026-0015", "receipt": "REC-2026-0010"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(46,'PAYMENT','PAY-2026-0011','COLLECT','Accounts Office','{"amount": "24500.00", "invoice": "INV-2026-0022", "receipt": "REC-2026-0011"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(47,'PAYMENT','PAY-2026-0012','COLLECT','Rajesh Sharma','{"amount": "25000.00", "invoice": "INV-2026-0024", "receipt": "REC-2026-0012"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(48,'PAYMENT','PAY-2026-0013','COLLECT','Counter Cashier','{"amount": "32000.00", "invoice": "INV-2026-0027", "receipt": "REC-2026-0013"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(49,'PAYMENT','PAY-2026-0014','COLLECT','Sunita Verma','{"amount": "12000.00", "invoice": "INV-2026-0030", "receipt": "REC-2026-0014"}','2026-11-04 17:46:33');
INSERT INTO "audit_logs" VALUES(50,'PAYMENT','PAY-2026-0015','COLLECT','Counter Cashier','{"amount": "16900.00", "invoice": "INV-2026-0033", "receipt": "REC-2026-0015"}','2026-11-04 17:46:33');
CREATE TABLE classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        grade_level INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
INSERT INTO "classes" VALUES(1,'Class 1-A',1,'2026-11-04 17:46:33');
INSERT INTO "classes" VALUES(2,'Class 1-B',1,'2026-11-04 17:46:33');
INSERT INTO "classes" VALUES(3,'Class 5-A',5,'2026-11-04 17:46:33');
INSERT INTO "classes" VALUES(4,'Class 5-B',5,'2026-11-04 17:46:33');
INSERT INTO "classes" VALUES(5,'Class 8-A',8,'2026-11-04 17:46:33');
INSERT INTO "classes" VALUES(6,'Class 9-A',9,'2026-11-04 17:46:33');
INSERT INTO "classes" VALUES(7,'Class 9-B',9,'2026-11-04 17:46:33');
INSERT INTO "classes" VALUES(8,'Class 10-A',10,'2026-11-04 17:46:33');
INSERT INTO "classes" VALUES(9,'Class 10-B',10,'2026-11-04 17:46:33');
INSERT INTO "classes" VALUES(10,'Class 11-Science',11,'2026-11-04 17:46:33');
INSERT INTO "classes" VALUES(11,'Class 11-Commerce',11,'2026-11-04 17:46:33');
INSERT INTO "classes" VALUES(12,'Class 12-Science',12,'2026-11-04 17:46:33');
CREATE TABLE discount_policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL UNIQUE,
        discount_type TEXT NOT NULL,
        value TEXT NOT NULL,
        applies_to_head_code TEXT,
        description TEXT DEFAULT ''
    );
INSERT INTO "discount_policies" VALUES(1,'Merit Scholarship 25%','MERIT_25','PERCENTAGE','25.00','TUITION','Top 5% percentile in academic assessments');
INSERT INTO "discount_policies" VALUES(2,'Merit Scholarship 50%','MERIT_50','PERCENTAGE','50.00','TUITION','Board examination and Olympiad rank holders');
INSERT INTO "discount_policies" VALUES(3,'Sibling Concession (₹1,500)','SIBLING_FLAT','FIXED','1500.00',NULL,'Concession for younger siblings in school');
INSERT INTO "discount_policies" VALUES(4,'Staff Ward Concession 50%','STAFF_50','PERCENTAGE','50.00','TUITION','Tuition waiver for faculty and school staff children');
INSERT INTO "discount_policies" VALUES(5,'RTE / EWS Fee Waiver 100%','RTE_100','PERCENTAGE','100.00','TUITION','Right to Education Act 25% reserved quota waiver');
INSERT INTO "discount_policies" VALUES(6,'Sports Quota Concession 30%','SPORTS_30','PERCENTAGE','30.00','TUITION','State/National level athlete scholarship');
CREATE TABLE fee_heads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        code TEXT NOT NULL UNIQUE,
        description TEXT DEFAULT '',
        is_recurring INTEGER NOT NULL DEFAULT 1,
        is_optional INTEGER NOT NULL DEFAULT 0
    );
INSERT INTO "fee_heads" VALUES(1,'Tuition Fee','TUITION','Core academic instruction & curriculum fee',1,0);
INSERT INTO "fee_heads" VALUES(2,'Computer & Smart Class Fee','LAB','Computer, AI lab and interactive smartboard fee',1,0);
INSERT INTO "fee_heads" VALUES(3,'Annual Development Fund','ANNUAL_DEV','School infrastructure and development fund',1,0);
INSERT INTO "fee_heads" VALUES(4,'Science Composite Lab Fee','SCIENCE_LAB','Physics, Chemistry and Biology laboratory charges',1,0);
INSERT INTO "fee_heads" VALUES(5,'Library & Digital Content','LIBRARY','Library access and digital learning subscription',1,0);
INSERT INTO "fee_heads" VALUES(6,'Sports & Co-Curricular','SPORTS','Athletic coaching, sports equipment & yoga',1,0);
INSERT INTO "fee_heads" VALUES(7,'School Bus Transport Fee','TRANSPORT','Route-wise GPS tracked bus transportation',1,1);
INSERT INTO "fee_heads" VALUES(8,'Hostel & Mess Boarding','HOSTEL','Boarding accommodation, meals and laundry',1,1);
INSERT INTO "fee_heads" VALUES(9,'Examination & Assessment','EXAM','Term assessment, printing and CBSE board papers',1,0);
INSERT INTO "fee_heads" VALUES(10,'Admission Registration','ADMISSION','One-time registration fee for new admissions',0,0);
CREATE TABLE fee_structure_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fee_structure_id INTEGER NOT NULL REFERENCES fee_structures(id) ON DELETE CASCADE,
        fee_head_id INTEGER NOT NULL REFERENCES fee_heads(id) ON DELETE RESTRICT,
        amount TEXT NOT NULL
    );
INSERT INTO "fee_structure_items" VALUES(1,1,1,'12000.00');
INSERT INTO "fee_structure_items" VALUES(2,1,2,'2500.00');
INSERT INTO "fee_structure_items" VALUES(3,1,3,'4000.00');
INSERT INTO "fee_structure_items" VALUES(4,1,4,'1500.00');
INSERT INTO "fee_structure_items" VALUES(5,1,5,'1000.00');
INSERT INTO "fee_structure_items" VALUES(6,1,6,'800.00');
INSERT INTO "fee_structure_items" VALUES(7,1,9,'600.00');
INSERT INTO "fee_structure_items" VALUES(8,1,7,'3500.00');
INSERT INTO "fee_structure_items" VALUES(9,1,8,'18000.00');
INSERT INTO "fee_structure_items" VALUES(10,2,1,'12000.00');
INSERT INTO "fee_structure_items" VALUES(11,2,2,'2500.00');
INSERT INTO "fee_structure_items" VALUES(12,2,3,'4000.00');
INSERT INTO "fee_structure_items" VALUES(13,2,4,'1500.00');
INSERT INTO "fee_structure_items" VALUES(14,2,5,'1000.00');
INSERT INTO "fee_structure_items" VALUES(15,2,6,'800.00');
INSERT INTO "fee_structure_items" VALUES(16,2,9,'600.00');
INSERT INTO "fee_structure_items" VALUES(17,2,7,'3500.00');
INSERT INTO "fee_structure_items" VALUES(18,2,8,'18000.00');
INSERT INTO "fee_structure_items" VALUES(19,3,1,'12000.00');
INSERT INTO "fee_structure_items" VALUES(20,3,2,'2500.00');
INSERT INTO "fee_structure_items" VALUES(21,3,3,'4000.00');
INSERT INTO "fee_structure_items" VALUES(22,3,4,'1500.00');
INSERT INTO "fee_structure_items" VALUES(23,3,5,'1000.00');
INSERT INTO "fee_structure_items" VALUES(24,3,6,'800.00');
INSERT INTO "fee_structure_items" VALUES(25,3,9,'600.00');
INSERT INTO "fee_structure_items" VALUES(26,3,7,'3500.00');
INSERT INTO "fee_structure_items" VALUES(27,3,8,'18000.00');
INSERT INTO "fee_structure_items" VALUES(28,4,1,'12000.00');
INSERT INTO "fee_structure_items" VALUES(29,4,2,'2500.00');
INSERT INTO "fee_structure_items" VALUES(30,4,3,'4000.00');
INSERT INTO "fee_structure_items" VALUES(31,4,4,'1500.00');
INSERT INTO "fee_structure_items" VALUES(32,4,5,'1000.00');
INSERT INTO "fee_structure_items" VALUES(33,4,6,'800.00');
INSERT INTO "fee_structure_items" VALUES(34,4,9,'600.00');
INSERT INTO "fee_structure_items" VALUES(35,4,7,'3500.00');
INSERT INTO "fee_structure_items" VALUES(36,4,8,'18000.00');
INSERT INTO "fee_structure_items" VALUES(37,5,1,'15000.00');
INSERT INTO "fee_structure_items" VALUES(38,5,2,'3000.00');
INSERT INTO "fee_structure_items" VALUES(39,5,3,'5000.00');
INSERT INTO "fee_structure_items" VALUES(40,5,4,'2000.00');
INSERT INTO "fee_structure_items" VALUES(41,5,5,'1200.00');
INSERT INTO "fee_structure_items" VALUES(42,5,6,'1000.00');
INSERT INTO "fee_structure_items" VALUES(43,5,9,'800.00');
INSERT INTO "fee_structure_items" VALUES(44,5,7,'4000.00');
INSERT INTO "fee_structure_items" VALUES(45,5,8,'20000.00');
INSERT INTO "fee_structure_items" VALUES(46,6,1,'15000.00');
INSERT INTO "fee_structure_items" VALUES(47,6,2,'3000.00');
INSERT INTO "fee_structure_items" VALUES(48,6,3,'5000.00');
INSERT INTO "fee_structure_items" VALUES(49,6,4,'2000.00');
INSERT INTO "fee_structure_items" VALUES(50,6,5,'1200.00');
INSERT INTO "fee_structure_items" VALUES(51,6,6,'1000.00');
INSERT INTO "fee_structure_items" VALUES(52,6,9,'800.00');
INSERT INTO "fee_structure_items" VALUES(53,6,7,'4000.00');
INSERT INTO "fee_structure_items" VALUES(54,6,8,'20000.00');
INSERT INTO "fee_structure_items" VALUES(55,7,1,'15000.00');
INSERT INTO "fee_structure_items" VALUES(56,7,2,'3000.00');
INSERT INTO "fee_structure_items" VALUES(57,7,3,'5000.00');
INSERT INTO "fee_structure_items" VALUES(58,7,4,'2000.00');
INSERT INTO "fee_structure_items" VALUES(59,7,5,'1200.00');
INSERT INTO "fee_structure_items" VALUES(60,7,6,'1000.00');
INSERT INTO "fee_structure_items" VALUES(61,7,9,'800.00');
INSERT INTO "fee_structure_items" VALUES(62,7,7,'4000.00');
INSERT INTO "fee_structure_items" VALUES(63,7,8,'20000.00');
INSERT INTO "fee_structure_items" VALUES(64,8,1,'9000.00');
INSERT INTO "fee_structure_items" VALUES(65,8,2,'1500.00');
INSERT INTO "fee_structure_items" VALUES(66,8,3,'3000.00');
INSERT INTO "fee_structure_items" VALUES(67,8,5,'800.00');
INSERT INTO "fee_structure_items" VALUES(68,8,6,'600.00');
INSERT INTO "fee_structure_items" VALUES(69,8,9,'500.00');
INSERT INTO "fee_structure_items" VALUES(70,8,7,'3000.00');
INSERT INTO "fee_structure_items" VALUES(71,8,8,'16000.00');
INSERT INTO "fee_structure_items" VALUES(72,9,1,'9000.00');
INSERT INTO "fee_structure_items" VALUES(73,9,2,'1500.00');
INSERT INTO "fee_structure_items" VALUES(74,9,3,'3000.00');
INSERT INTO "fee_structure_items" VALUES(75,9,5,'800.00');
INSERT INTO "fee_structure_items" VALUES(76,9,6,'600.00');
INSERT INTO "fee_structure_items" VALUES(77,9,9,'500.00');
INSERT INTO "fee_structure_items" VALUES(78,9,7,'3000.00');
INSERT INTO "fee_structure_items" VALUES(79,9,8,'16000.00');
INSERT INTO "fee_structure_items" VALUES(80,10,1,'9000.00');
INSERT INTO "fee_structure_items" VALUES(81,10,2,'1500.00');
INSERT INTO "fee_structure_items" VALUES(82,10,3,'3000.00');
INSERT INTO "fee_structure_items" VALUES(83,10,5,'800.00');
INSERT INTO "fee_structure_items" VALUES(84,10,6,'600.00');
INSERT INTO "fee_structure_items" VALUES(85,10,9,'500.00');
INSERT INTO "fee_structure_items" VALUES(86,10,7,'3000.00');
INSERT INTO "fee_structure_items" VALUES(87,10,8,'16000.00');
INSERT INTO "fee_structure_items" VALUES(88,11,1,'9000.00');
INSERT INTO "fee_structure_items" VALUES(89,11,2,'1500.00');
INSERT INTO "fee_structure_items" VALUES(90,11,3,'3000.00');
INSERT INTO "fee_structure_items" VALUES(91,11,5,'800.00');
INSERT INTO "fee_structure_items" VALUES(92,11,6,'600.00');
INSERT INTO "fee_structure_items" VALUES(93,11,9,'500.00');
INSERT INTO "fee_structure_items" VALUES(94,11,7,'3000.00');
INSERT INTO "fee_structure_items" VALUES(95,11,8,'16000.00');
INSERT INTO "fee_structure_items" VALUES(96,12,1,'9000.00');
INSERT INTO "fee_structure_items" VALUES(97,12,2,'1500.00');
INSERT INTO "fee_structure_items" VALUES(98,12,3,'3000.00');
INSERT INTO "fee_structure_items" VALUES(99,12,5,'800.00');
INSERT INTO "fee_structure_items" VALUES(100,12,6,'600.00');
INSERT INTO "fee_structure_items" VALUES(101,12,9,'500.00');
INSERT INTO "fee_structure_items" VALUES(102,12,7,'3000.00');
INSERT INTO "fee_structure_items" VALUES(103,12,8,'16000.00');
CREATE TABLE fee_structures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
        academic_year TEXT NOT NULL,
        term TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(class_id, academic_year, term)
    );
INSERT INTO "fee_structures" VALUES(1,'Class 10-A Term-1 (Apr-Sep 2026)',8,'2026-2027','TERM_1','2026-11-04 17:46:33');
INSERT INTO "fee_structures" VALUES(2,'Class 10-B Term-1 (Apr-Sep 2026)',9,'2026-2027','TERM_1','2026-11-04 17:46:33');
INSERT INTO "fee_structures" VALUES(3,'Class 9-A Term-1 (Apr-Sep 2026)',6,'2026-2027','TERM_1','2026-11-04 17:46:33');
INSERT INTO "fee_structures" VALUES(4,'Class 9-B Term-1 (Apr-Sep 2026)',7,'2026-2027','TERM_1','2026-11-04 17:46:33');
INSERT INTO "fee_structures" VALUES(5,'Class 11-Science Term-1 (Apr-Sep 2026)',10,'2026-2027','TERM_1','2026-11-04 17:46:33');
INSERT INTO "fee_structures" VALUES(6,'Class 11-Commerce Term-1 (Apr-Sep 2026)',11,'2026-2027','TERM_1','2026-11-04 17:46:33');
INSERT INTO "fee_structures" VALUES(7,'Class 12-Science Term-1 (Apr-Sep 2026)',12,'2026-2027','TERM_1','2026-11-04 17:46:33');
INSERT INTO "fee_structures" VALUES(8,'Class 8-A Term-1 (Apr-Sep 2026)',5,'2026-2027','TERM_1','2026-11-04 17:46:33');
INSERT INTO "fee_structures" VALUES(9,'Class 5-A Term-1 (Apr-Sep 2026)',3,'2026-2027','TERM_1','2026-11-04 17:46:33');
INSERT INTO "fee_structures" VALUES(10,'Class 5-B Term-1 (Apr-Sep 2026)',4,'2026-2027','TERM_1','2026-11-04 17:46:33');
INSERT INTO "fee_structures" VALUES(11,'Class 1-A Term-1 (Apr-Sep 2026)',1,'2026-2027','TERM_1','2026-11-04 17:46:33');
INSERT INTO "fee_structures" VALUES(12,'Class 1-B Term-1 (Apr-Sep 2026)',2,'2026-2027','TERM_1','2026-11-04 17:46:33');
CREATE TABLE invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
        fee_head_id INTEGER NOT NULL REFERENCES fee_heads(id),
        head_name TEXT NOT NULL,
        head_code TEXT NOT NULL,
        amount TEXT NOT NULL,
        discount_amount TEXT NOT NULL DEFAULT '0.00',
        net_amount TEXT NOT NULL
    );
INSERT INTO "invoice_items" VALUES(1,1,1,'Tuition Fee','TUITION','12000.00','3000.00','9000.00');
INSERT INTO "invoice_items" VALUES(2,1,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(3,1,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(4,1,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(5,1,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(6,1,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(7,1,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(8,1,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(9,2,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(10,2,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(11,2,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(12,2,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(13,2,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(14,2,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(15,2,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(16,3,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(17,3,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(18,3,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(19,3,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(20,3,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(21,3,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(22,3,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(23,3,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(24,3,8,'Hostel & Mess Boarding','HOSTEL','18000.00','0.00','18000.00');
INSERT INTO "invoice_items" VALUES(25,4,1,'Tuition Fee','TUITION','12000.00','1500.00','10500.00');
INSERT INTO "invoice_items" VALUES(26,4,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(27,4,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(28,4,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(29,4,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(30,4,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(31,4,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(32,5,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(33,5,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(34,5,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(35,5,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(36,5,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(37,5,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(38,5,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(39,5,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(40,6,1,'Tuition Fee','TUITION','12000.00','6000.00','6000.00');
INSERT INTO "invoice_items" VALUES(41,6,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(42,6,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(43,6,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(44,6,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(45,6,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(46,6,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(47,6,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(48,7,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(49,7,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(50,7,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(51,7,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(52,7,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(53,7,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(54,7,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(55,8,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(56,8,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(57,8,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(58,8,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(59,8,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(60,8,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(61,8,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(62,8,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(63,9,1,'Tuition Fee','TUITION','12000.00','6000.00','6000.00');
INSERT INTO "invoice_items" VALUES(64,9,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(65,9,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(66,9,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(67,9,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(68,9,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(69,9,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(70,10,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(71,10,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(72,10,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(73,10,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(74,10,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(75,10,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(76,10,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(77,10,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(78,11,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(79,11,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(80,11,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(81,11,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(82,11,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(83,11,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(84,11,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(85,11,8,'Hostel & Mess Boarding','HOSTEL','18000.00','0.00','18000.00');
INSERT INTO "invoice_items" VALUES(86,12,1,'Tuition Fee','TUITION','12000.00','3000.00','9000.00');
INSERT INTO "invoice_items" VALUES(87,12,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(88,12,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(89,12,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(90,12,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(91,12,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(92,12,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(93,12,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(94,13,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(95,13,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(96,13,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(97,13,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(98,13,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(99,13,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(100,13,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(101,13,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(102,14,1,'Tuition Fee','TUITION','12000.00','1500.00','10500.00');
INSERT INTO "invoice_items" VALUES(103,14,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(104,14,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(105,14,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(106,14,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(107,14,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(108,14,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(109,15,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(110,15,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(111,15,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(112,15,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(113,15,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(114,15,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(115,15,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(116,15,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(117,16,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(118,16,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(119,16,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(120,16,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(121,16,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(122,16,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(123,16,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(124,17,1,'Tuition Fee','TUITION','12000.00','3600.00','8400.00');
INSERT INTO "invoice_items" VALUES(125,17,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(126,17,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(127,17,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(128,17,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(129,17,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(130,17,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(131,17,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(132,17,8,'Hostel & Mess Boarding','HOSTEL','18000.00','0.00','18000.00');
INSERT INTO "invoice_items" VALUES(133,18,1,'Tuition Fee','TUITION','12000.00','12000.00','0.00');
INSERT INTO "invoice_items" VALUES(134,18,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(135,18,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(136,18,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(137,18,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(138,18,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(139,18,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(140,19,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(141,19,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(142,19,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(143,19,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(144,19,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(145,19,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(146,19,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(147,19,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(148,20,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(149,20,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(150,20,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(151,20,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(152,20,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(153,20,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(154,20,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(155,21,1,'Tuition Fee','TUITION','12000.00','0.00','12000.00');
INSERT INTO "invoice_items" VALUES(156,21,2,'Computer & Smart Class Fee','LAB','2500.00','0.00','2500.00');
INSERT INTO "invoice_items" VALUES(157,21,3,'Annual Development Fund','ANNUAL_DEV','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(158,21,4,'Science Composite Lab Fee','SCIENCE_LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(159,21,5,'Library & Digital Content','LIBRARY','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(160,21,6,'Sports & Co-Curricular','SPORTS','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(161,21,9,'Examination & Assessment','EXAM','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(162,21,7,'School Bus Transport Fee','TRANSPORT','3500.00','0.00','3500.00');
INSERT INTO "invoice_items" VALUES(163,22,1,'Tuition Fee','TUITION','15000.00','7500.00','7500.00');
INSERT INTO "invoice_items" VALUES(164,22,2,'Computer & Smart Class Fee','LAB','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(165,22,3,'Annual Development Fund','ANNUAL_DEV','5000.00','0.00','5000.00');
INSERT INTO "invoice_items" VALUES(166,22,4,'Science Composite Lab Fee','SCIENCE_LAB','2000.00','0.00','2000.00');
INSERT INTO "invoice_items" VALUES(167,22,5,'Library & Digital Content','LIBRARY','1200.00','0.00','1200.00');
INSERT INTO "invoice_items" VALUES(168,22,6,'Sports & Co-Curricular','SPORTS','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(169,22,9,'Examination & Assessment','EXAM','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(170,22,7,'School Bus Transport Fee','TRANSPORT','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(171,23,1,'Tuition Fee','TUITION','15000.00','0.00','15000.00');
INSERT INTO "invoice_items" VALUES(172,23,2,'Computer & Smart Class Fee','LAB','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(173,23,3,'Annual Development Fund','ANNUAL_DEV','5000.00','0.00','5000.00');
INSERT INTO "invoice_items" VALUES(174,23,4,'Science Composite Lab Fee','SCIENCE_LAB','2000.00','0.00','2000.00');
INSERT INTO "invoice_items" VALUES(175,23,5,'Library & Digital Content','LIBRARY','1200.00','0.00','1200.00');
INSERT INTO "invoice_items" VALUES(176,23,6,'Sports & Co-Curricular','SPORTS','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(177,23,9,'Examination & Assessment','EXAM','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(178,24,1,'Tuition Fee','TUITION','15000.00','0.00','15000.00');
INSERT INTO "invoice_items" VALUES(179,24,2,'Computer & Smart Class Fee','LAB','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(180,24,3,'Annual Development Fund','ANNUAL_DEV','5000.00','0.00','5000.00');
INSERT INTO "invoice_items" VALUES(181,24,4,'Science Composite Lab Fee','SCIENCE_LAB','2000.00','0.00','2000.00');
INSERT INTO "invoice_items" VALUES(182,24,5,'Library & Digital Content','LIBRARY','1200.00','0.00','1200.00');
INSERT INTO "invoice_items" VALUES(183,24,6,'Sports & Co-Curricular','SPORTS','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(184,24,9,'Examination & Assessment','EXAM','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(185,24,7,'School Bus Transport Fee','TRANSPORT','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(186,24,8,'Hostel & Mess Boarding','HOSTEL','20000.00','0.00','20000.00');
INSERT INTO "invoice_items" VALUES(187,25,1,'Tuition Fee','TUITION','15000.00','0.00','15000.00');
INSERT INTO "invoice_items" VALUES(188,25,2,'Computer & Smart Class Fee','LAB','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(189,25,3,'Annual Development Fund','ANNUAL_DEV','5000.00','0.00','5000.00');
INSERT INTO "invoice_items" VALUES(190,25,4,'Science Composite Lab Fee','SCIENCE_LAB','2000.00','0.00','2000.00');
INSERT INTO "invoice_items" VALUES(191,25,5,'Library & Digital Content','LIBRARY','1200.00','0.00','1200.00');
INSERT INTO "invoice_items" VALUES(192,25,6,'Sports & Co-Curricular','SPORTS','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(193,25,9,'Examination & Assessment','EXAM','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(194,25,7,'School Bus Transport Fee','TRANSPORT','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(195,26,1,'Tuition Fee','TUITION','15000.00','7500.00','7500.00');
INSERT INTO "invoice_items" VALUES(196,26,2,'Computer & Smart Class Fee','LAB','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(197,26,3,'Annual Development Fund','ANNUAL_DEV','5000.00','0.00','5000.00');
INSERT INTO "invoice_items" VALUES(198,26,4,'Science Composite Lab Fee','SCIENCE_LAB','2000.00','0.00','2000.00');
INSERT INTO "invoice_items" VALUES(199,26,5,'Library & Digital Content','LIBRARY','1200.00','0.00','1200.00');
INSERT INTO "invoice_items" VALUES(200,26,6,'Sports & Co-Curricular','SPORTS','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(201,26,9,'Examination & Assessment','EXAM','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(202,27,1,'Tuition Fee','TUITION','15000.00','0.00','15000.00');
INSERT INTO "invoice_items" VALUES(203,27,2,'Computer & Smart Class Fee','LAB','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(204,27,3,'Annual Development Fund','ANNUAL_DEV','5000.00','0.00','5000.00');
INSERT INTO "invoice_items" VALUES(205,27,4,'Science Composite Lab Fee','SCIENCE_LAB','2000.00','0.00','2000.00');
INSERT INTO "invoice_items" VALUES(206,27,5,'Library & Digital Content','LIBRARY','1200.00','0.00','1200.00');
INSERT INTO "invoice_items" VALUES(207,27,6,'Sports & Co-Curricular','SPORTS','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(208,27,9,'Examination & Assessment','EXAM','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(209,27,7,'School Bus Transport Fee','TRANSPORT','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(210,28,1,'Tuition Fee','TUITION','15000.00','0.00','15000.00');
INSERT INTO "invoice_items" VALUES(211,28,2,'Computer & Smart Class Fee','LAB','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(212,28,3,'Annual Development Fund','ANNUAL_DEV','5000.00','0.00','5000.00');
INSERT INTO "invoice_items" VALUES(213,28,4,'Science Composite Lab Fee','SCIENCE_LAB','2000.00','0.00','2000.00');
INSERT INTO "invoice_items" VALUES(214,28,5,'Library & Digital Content','LIBRARY','1200.00','0.00','1200.00');
INSERT INTO "invoice_items" VALUES(215,28,6,'Sports & Co-Curricular','SPORTS','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(216,28,9,'Examination & Assessment','EXAM','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(217,29,1,'Tuition Fee','TUITION','15000.00','0.00','15000.00');
INSERT INTO "invoice_items" VALUES(218,29,2,'Computer & Smart Class Fee','LAB','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(219,29,3,'Annual Development Fund','ANNUAL_DEV','5000.00','0.00','5000.00');
INSERT INTO "invoice_items" VALUES(220,29,4,'Science Composite Lab Fee','SCIENCE_LAB','2000.00','0.00','2000.00');
INSERT INTO "invoice_items" VALUES(221,29,5,'Library & Digital Content','LIBRARY','1200.00','0.00','1200.00');
INSERT INTO "invoice_items" VALUES(222,29,6,'Sports & Co-Curricular','SPORTS','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(223,29,9,'Examination & Assessment','EXAM','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(224,29,7,'School Bus Transport Fee','TRANSPORT','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(225,30,1,'Tuition Fee','TUITION','15000.00','3750.00','11250.00');
INSERT INTO "invoice_items" VALUES(226,30,2,'Computer & Smart Class Fee','LAB','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(227,30,3,'Annual Development Fund','ANNUAL_DEV','5000.00','0.00','5000.00');
INSERT INTO "invoice_items" VALUES(228,30,4,'Science Composite Lab Fee','SCIENCE_LAB','2000.00','0.00','2000.00');
INSERT INTO "invoice_items" VALUES(229,30,5,'Library & Digital Content','LIBRARY','1200.00','0.00','1200.00');
INSERT INTO "invoice_items" VALUES(230,30,6,'Sports & Co-Curricular','SPORTS','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(231,30,9,'Examination & Assessment','EXAM','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(232,31,1,'Tuition Fee','TUITION','15000.00','0.00','15000.00');
INSERT INTO "invoice_items" VALUES(233,31,2,'Computer & Smart Class Fee','LAB','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(234,31,3,'Annual Development Fund','ANNUAL_DEV','5000.00','0.00','5000.00');
INSERT INTO "invoice_items" VALUES(235,31,4,'Science Composite Lab Fee','SCIENCE_LAB','2000.00','0.00','2000.00');
INSERT INTO "invoice_items" VALUES(236,31,5,'Library & Digital Content','LIBRARY','1200.00','0.00','1200.00');
INSERT INTO "invoice_items" VALUES(237,31,6,'Sports & Co-Curricular','SPORTS','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(238,31,9,'Examination & Assessment','EXAM','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(239,31,7,'School Bus Transport Fee','TRANSPORT','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(240,32,1,'Tuition Fee','TUITION','15000.00','0.00','15000.00');
INSERT INTO "invoice_items" VALUES(241,32,2,'Computer & Smart Class Fee','LAB','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(242,32,3,'Annual Development Fund','ANNUAL_DEV','5000.00','0.00','5000.00');
INSERT INTO "invoice_items" VALUES(243,32,4,'Science Composite Lab Fee','SCIENCE_LAB','2000.00','0.00','2000.00');
INSERT INTO "invoice_items" VALUES(244,32,5,'Library & Digital Content','LIBRARY','1200.00','0.00','1200.00');
INSERT INTO "invoice_items" VALUES(245,32,6,'Sports & Co-Curricular','SPORTS','1000.00','0.00','1000.00');
INSERT INTO "invoice_items" VALUES(246,32,9,'Examination & Assessment','EXAM','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(247,32,7,'School Bus Transport Fee','TRANSPORT','4000.00','0.00','4000.00');
INSERT INTO "invoice_items" VALUES(248,32,8,'Hostel & Mess Boarding','HOSTEL','20000.00','0.00','20000.00');
INSERT INTO "invoice_items" VALUES(249,33,1,'Tuition Fee','TUITION','9000.00','1500.00','7500.00');
INSERT INTO "invoice_items" VALUES(250,33,2,'Computer & Smart Class Fee','LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(251,33,3,'Annual Development Fund','ANNUAL_DEV','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(252,33,5,'Library & Digital Content','LIBRARY','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(253,33,6,'Sports & Co-Curricular','SPORTS','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(254,33,9,'Examination & Assessment','EXAM','500.00','0.00','500.00');
INSERT INTO "invoice_items" VALUES(255,33,7,'School Bus Transport Fee','TRANSPORT','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(256,34,1,'Tuition Fee','TUITION','9000.00','0.00','9000.00');
INSERT INTO "invoice_items" VALUES(257,34,2,'Computer & Smart Class Fee','LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(258,34,3,'Annual Development Fund','ANNUAL_DEV','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(259,34,5,'Library & Digital Content','LIBRARY','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(260,34,6,'Sports & Co-Curricular','SPORTS','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(261,34,9,'Examination & Assessment','EXAM','500.00','0.00','500.00');
INSERT INTO "invoice_items" VALUES(262,35,1,'Tuition Fee','TUITION','9000.00','0.00','9000.00');
INSERT INTO "invoice_items" VALUES(263,35,2,'Computer & Smart Class Fee','LAB','1500.00','0.00','1500.00');
INSERT INTO "invoice_items" VALUES(264,35,3,'Annual Development Fund','ANNUAL_DEV','3000.00','0.00','3000.00');
INSERT INTO "invoice_items" VALUES(265,35,5,'Library & Digital Content','LIBRARY','800.00','0.00','800.00');
INSERT INTO "invoice_items" VALUES(266,35,6,'Sports & Co-Curricular','SPORTS','600.00','0.00','600.00');
INSERT INTO "invoice_items" VALUES(267,35,9,'Examination & Assessment','EXAM','500.00','0.00','500.00');
INSERT INTO "invoice_items" VALUES(268,35,7,'School Bus Transport Fee','TRANSPORT','3000.00','0.00','3000.00');
CREATE TABLE invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT NOT NULL UNIQUE,
        student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE RESTRICT,
        academic_year TEXT NOT NULL,
        term TEXT NOT NULL,
        issue_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        subtotal TEXT NOT NULL,
        discount_total TEXT NOT NULL DEFAULT '0.00',
        late_fee TEXT NOT NULL DEFAULT '0.00',
        total_payable TEXT NOT NULL,
        paid_amount TEXT NOT NULL DEFAULT '0.00',
        status TEXT NOT NULL DEFAULT 'UNPAID',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
INSERT INTO "invoices" VALUES(1,'INV-2026-0001','ADM-2026-001','2026-2027','TERM_1','2026-11-04','2026-11-24','25900.00','3000.00','0.00','22900.00','15000.00','PARTIALLY_PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(2,'INV-2026-0002','ADM-2026-002','2026-2027','TERM_1','2026-11-04','2026-11-24','22400.00','0.00','0.00','22400.00','22400.00','PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(3,'INV-2026-0003','ADM-2026-003','2026-2027','TERM_1','2026-11-04','2026-11-24','43900.00','0.00','0.00','43900.00','20000.00','PARTIALLY_PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(4,'INV-2026-0004','ADM-2026-004','2026-2027','TERM_1','2026-11-04','2026-10-20','22400.00','1500.00','75.00','20975.00','0.00','OVERDUE','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(5,'INV-2026-0005','ADM-2026-005','2026-2027','TERM_1','2026-11-04','2026-11-24','25900.00','0.00','0.00','25900.00','25900.00','PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(6,'INV-2026-0006','ADM-2026-006','2026-2027','TERM_1','2026-11-04','2026-11-24','25900.00','6000.00','0.00','19900.00','19900.00','PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(7,'INV-2026-0007','ADM-2026-007','2026-2027','TERM_1','2026-11-04','2026-10-20','22400.00','0.00','75.00','22475.00','0.00','OVERDUE','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(8,'INV-2026-0008','ADM-2026-008','2026-2027','TERM_1','2026-11-04','2026-11-24','25900.00','0.00','0.00','25900.00','12000.00','PARTIALLY_PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(9,'INV-2026-0009','ADM-2026-009','2026-2027','TERM_1','2026-11-04','2026-11-24','22400.00','6000.00','0.00','16400.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(10,'INV-2026-0010','ADM-2026-010','2026-2027','TERM_1','2026-11-04','2026-11-24','25900.00','0.00','0.00','25900.00','25900.00','PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(11,'INV-2026-0011','ADM-2026-011','2026-2027','TERM_1','2026-11-04','2026-10-20','40400.00','0.00','75.00','40475.00','0.00','OVERDUE','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(12,'INV-2026-0012','ADM-2026-012','2026-2027','TERM_1','2026-11-04','2026-11-24','25900.00','3000.00','0.00','22900.00','10000.00','PARTIALLY_PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(13,'INV-2026-0013','ADM-2026-013','2026-2027','TERM_1','2026-11-04','2026-11-24','25900.00','0.00','0.00','25900.00','25900.00','PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(14,'INV-2026-0014','ADM-2026-014','2026-2027','TERM_1','2026-11-04','2026-11-24','22400.00','1500.00','0.00','20900.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(15,'INV-2026-0015','ADM-2026-015','2026-2027','TERM_1','2026-11-04','2026-11-24','25900.00','0.00','0.00','25900.00','8000.00','PARTIALLY_PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(16,'INV-2026-0016','ADM-2026-016','2026-2027','TERM_1','2026-11-04','2026-10-20','22400.00','0.00','75.00','22475.00','0.00','OVERDUE','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(17,'INV-2026-0017','ADM-2026-017','2026-2027','TERM_1','2026-11-04','2026-11-24','43900.00','3600.00','0.00','40300.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(18,'INV-2026-0018','ADM-2026-018','2026-2027','TERM_1','2026-11-04','2026-11-24','22400.00','12000.00','0.00','10400.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(19,'INV-2026-0019','ADM-2026-019','2026-2027','TERM_1','2026-11-04','2026-11-24','25900.00','0.00','0.00','25900.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(20,'INV-2026-0020','ADM-2026-020','2026-2027','TERM_1','2026-11-04','2026-11-24','22400.00','0.00','0.00','22400.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(21,'INV-2026-0021','ADM-2026-021','2026-2027','TERM_1','2026-11-04','2026-11-24','25900.00','0.00','0.00','25900.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(22,'INV-2026-0022','ADM-2026-022','2026-2027','TERM_1','2026-11-04','2026-11-24','32000.00','7500.00','0.00','24500.00','24500.00','PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(23,'INV-2026-0023','ADM-2026-023','2026-2027','TERM_1','2026-11-04','2026-10-20','28000.00','0.00','75.00','28075.00','0.00','OVERDUE','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(24,'INV-2026-0024','ADM-2026-024','2026-2027','TERM_1','2026-11-04','2026-11-24','52000.00','0.00','0.00','52000.00','25000.00','PARTIALLY_PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(25,'INV-2026-0025','ADM-2026-025','2026-2027','TERM_1','2026-11-04','2026-11-24','32000.00','0.00','0.00','32000.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(26,'INV-2026-0026','ADM-2026-026','2026-2027','TERM_1','2026-11-04','2026-11-24','28000.00','7500.00','0.00','20500.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(27,'INV-2026-0027','ADM-2026-027','2026-2027','TERM_1','2026-11-04','2026-11-24','32000.00','0.00','0.00','32000.00','32000.00','PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(28,'INV-2026-0028','ADM-2026-028','2026-2027','TERM_1','2026-11-04','2026-10-20','28000.00','0.00','75.00','28075.00','0.00','OVERDUE','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(29,'INV-2026-0029','ADM-2026-029','2026-2027','TERM_1','2026-11-04','2026-11-24','32000.00','0.00','0.00','32000.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(30,'INV-2026-0030','ADM-2026-030','2026-2027','TERM_1','2026-11-04','2026-11-24','28000.00','3750.00','0.00','24250.00','12000.00','PARTIALLY_PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(31,'INV-2026-0031','ADM-2026-031','2026-2027','TERM_1','2026-11-04','2026-11-24','32000.00','0.00','0.00','32000.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(32,'INV-2026-0032','ADM-2026-032','2026-2027','TERM_1','2026-11-04','2026-11-24','52000.00','0.00','0.00','52000.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(33,'INV-2026-0033','ADM-2026-033','2026-2027','TERM_1','2026-11-04','2026-11-24','18400.00','1500.00','0.00','16900.00','16900.00','PAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(34,'INV-2026-0034','ADM-2026-034','2026-2027','TERM_1','2026-11-04','2026-11-24','15400.00','0.00','0.00','15400.00','0.00','UNPAID','2026-11-04 17:46:33');
INSERT INTO "invoices" VALUES(35,'INV-2026-0035','ADM-2026-035','2026-2027','TERM_1','2026-11-04','2026-11-24','18400.00','0.00','0.00','18400.00','0.00','UNPAID','2026-11-04 17:46:33');
CREATE TABLE payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_ref TEXT NOT NULL UNIQUE,
        invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE RESTRICT,
        amount TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        transaction_id TEXT NOT NULL,
        payment_date TIMESTAMP NOT NULL,
        cashier_name TEXT NOT NULL,
        notes TEXT DEFAULT ''
    );
INSERT INTO "payments" VALUES(1,'PAY-2026-0001',1,'15000.00','UPI','UPI/GPay/202604019921234','2026-11-04T23:16:33.487133','Sunita Verma','Term-1 advance via Google Pay');
INSERT INTO "payments" VALUES(2,'PAY-2026-0002',2,'22400.00','NET_BANKING','HDFC/NEFT/202604058811','2026-11-04T23:16:33.491896','Accounts Office','Full payment via HDFC NetBanking');
INSERT INTO "payments" VALUES(3,'PAY-2026-0003',3,'20000.00','CHEQUE_DD','CHQ-442109-SBI-DELHI','2026-11-04T23:16:33.496533','Rajesh Sharma','Cheque drawn on SBI Main Branch');
INSERT INTO "payments" VALUES(4,'PAY-2026-0004',5,'25900.00','UPI','UPI/PhonePe/2026041044321','2026-11-04T23:16:33.501468','Sunita Verma','Full Term-1 settlement via PhonePe');
INSERT INTO "payments" VALUES(5,'PAY-2026-0005',6,'19900.00','CASH','CASH-COUNTER-044','2026-11-04T23:16:33.506308','Counter Cashier','Counter cash receipt issued');
INSERT INTO "payments" VALUES(6,'PAY-2026-0006',8,'12000.00','CARD','POS/HDFC/998822','2026-11-04T23:16:33.510990','Counter Cashier','RuPay Debit Card payment at counter');
INSERT INTO "payments" VALUES(7,'PAY-2026-0007',10,'25900.00','UPI','UPI/Paytm/202604147761','2026-11-04T23:16:33.515562','Sunita Verma','Paytm UPI settlement');
INSERT INTO "payments" VALUES(8,'PAY-2026-0008',12,'10000.00','NET_BANKING','ICICI/IMPS/20260415332','2026-11-04T23:16:33.520203','Accounts Office','ICICI IMPS Transfer');
INSERT INTO "payments" VALUES(9,'PAY-2026-0009',13,'25900.00','CASH','CASH-COUNTER-098','2026-11-04T23:16:33.524789','Counter Cashier','Cash deposit at fee window');
INSERT INTO "payments" VALUES(10,'PAY-2026-0010',15,'8000.00','UPI','UPI/BHIM/20260416991','2026-11-04T23:16:33.529402','Sunita Verma','BHIM UPI payment (1st installment)');
INSERT INTO "payments" VALUES(11,'PAY-2026-0011',22,'24500.00','NET_BANKING','AXIS/NEFT/20260418554','2026-11-04T23:16:33.534021','Accounts Office','Axis Bank NEFT wire');
INSERT INTO "payments" VALUES(12,'PAY-2026-0012',24,'25000.00','CHEQUE_DD','CHQ-778811-PNB-NOIDA','2026-11-04T23:16:33.539070','Rajesh Sharma','Boarding & Tuition fees paid by Cheque');
INSERT INTO "payments" VALUES(13,'PAY-2026-0013',27,'32000.00','CARD','POS/SBI/334411','2026-11-04T23:16:33.543955','Counter Cashier','Visa card transaction at POS terminal');
INSERT INTO "payments" VALUES(14,'PAY-2026-0014',30,'12000.00','UPI','UPI/GPay/20260420112','2026-11-04T23:16:33.548511','Sunita Verma','Google Pay transaction');
INSERT INTO "payments" VALUES(15,'PAY-2026-0015',33,'16900.00','CASH','CASH-COUNTER-142','2026-11-04T23:16:33.553064','Counter Cashier','Fee counter collection');
CREATE TABLE receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_number TEXT NOT NULL UNIQUE,
        payment_id INTEGER NOT NULL REFERENCES payments(id) ON DELETE RESTRICT,
        receipt_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
INSERT INTO "receipts" VALUES(1,'REC-2026-0001',1,'692dda675801bf5eaea38c8852bee2027e9ac28301762ef5b7a45f4ec7cf804d','2026-11-04T23:16:33.487133');
INSERT INTO "receipts" VALUES(2,'REC-2026-0002',2,'31d465ed8df6be2d0f6edd0366b3e73e4e5ad77c78f0034ab75b14d5b90c5001','2026-11-04T23:16:33.491896');
INSERT INTO "receipts" VALUES(3,'REC-2026-0003',3,'e4c3c0b112b2dcca5c61638272f8708fa4c611e536ad341a305f9af18fdf3950','2026-11-04T23:16:33.496533');
INSERT INTO "receipts" VALUES(4,'REC-2026-0004',4,'3f3a73a0c87fd76a4b9b7d92b5f0d53b99c15d36cd97855f93cc0689665f16c4','2026-11-04T23:16:33.501468');
INSERT INTO "receipts" VALUES(5,'REC-2026-0005',5,'b1410dd7f844d798723f4267647c7c1ab33596358901c7b4185ce92e76f5a2c7','2026-11-04T23:16:33.506308');
INSERT INTO "receipts" VALUES(6,'REC-2026-0006',6,'77729955877d80e36196e0aec603c23cd9c1dc9287bbd54bc82c9f7d0c510b24','2026-11-04T23:16:33.510990');
INSERT INTO "receipts" VALUES(7,'REC-2026-0007',7,'f6b0c3699d2d131935d571dba021eceef7ea2ee96df3f747f6cc0a281c5e66fb','2026-11-04T23:16:33.515562');
INSERT INTO "receipts" VALUES(8,'REC-2026-0008',8,'c95dcaa84caeeaa300bbabbaac4bf0038d573bfb985554f529842a8fa502b4bb','2026-11-04T23:16:33.520203');
INSERT INTO "receipts" VALUES(9,'REC-2026-0009',9,'077183a53fdac7d8ad741fe5380cc5d43f13bdb4fd2a0c20db6e8e94f078e005','2026-11-04T23:16:33.524789');
INSERT INTO "receipts" VALUES(10,'REC-2026-0010',10,'54484ea11447f8bae9939cea4ccf0863e5444df7412f2e006b6871be2e5482f1','2026-11-04T23:16:33.529402');
INSERT INTO "receipts" VALUES(11,'REC-2026-0011',11,'b411d0d37cfa1e2ac66db465f90ed71e4fb078185c63b6ce81148070f10c2887','2026-11-04T23:16:33.534021');
INSERT INTO "receipts" VALUES(12,'REC-2026-0012',12,'9ce69fd31bea12e4b622707725d13c858a527fad5b7be2a3b88addb47e6177ed','2026-11-04T23:16:33.539070');
INSERT INTO "receipts" VALUES(13,'REC-2026-0013',13,'d75a5dbf2dfafa1fafe6483a8e07f76f74a277d05c50e2a7585f1f3eb81df1b2','2026-11-04T23:16:33.543955');
INSERT INTO "receipts" VALUES(14,'REC-2026-0014',14,'60128146877d3c9bb0c55ebd595a87ed4c1b4b29e8baab81da32f766fbc95d94','2026-11-04T23:16:33.548511');
INSERT INTO "receipts" VALUES(15,'REC-2026-0015',15,'88e1841b0ba8dc320ec96c3cd57b4dc8c3de28382e0fdc40b5069d3de9a4f66d','2026-11-04T23:16:33.553064');
CREATE TABLE student_discounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
        discount_policy_id INTEGER NOT NULL REFERENCES discount_policies(id) ON DELETE CASCADE,
        academic_year TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(student_id, discount_policy_id, academic_year)
    );
INSERT INTO "student_discounts" VALUES(1,'ADM-2026-001',1,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(2,'ADM-2026-004',3,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(3,'ADM-2026-006',2,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(4,'ADM-2026-009',4,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(5,'ADM-2026-012',1,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(6,'ADM-2026-014',3,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(7,'ADM-2026-017',6,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(8,'ADM-2026-018',5,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(9,'ADM-2026-022',2,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(10,'ADM-2026-026',4,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(11,'ADM-2026-030',1,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(12,'ADM-2026-033',3,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(13,'ADM-2026-039',5,'2026-2027','2026-11-04 17:46:33');
INSERT INTO "student_discounts" VALUES(14,'ADM-2026-043',3,'2026-2027','2026-11-04 17:46:33');
CREATE TABLE students (
        student_id TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        class_id INTEGER NOT NULL REFERENCES classes(id) ON DELETE RESTRICT,
        parent_name TEXT NOT NULL,
        parent_email TEXT NOT NULL,
        parent_phone TEXT NOT NULL,
        is_transport_enrolled INTEGER NOT NULL DEFAULT 0,
        is_hostel_enrolled INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL DEFAULT 'ACTIVE',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
INSERT INTO "students" VALUES('ADM-2026-001','Aarav','Sharma',8,'Rajesh Sharma','rajesh.sharma@example.com','+91 98110 12345',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-002','Priya','Patel',8,'Sunita Patel','sunita.patel@example.com','+91 98220 23456',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-003','Rohan','Verma',8,'Anil Verma','anil.verma@example.com','+91 98330 34567',1,1,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-004','Ananya','Iyer',8,'S. K. Iyer','sk.iyer@example.com','+91 98440 45678',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-005','Kabir','Singh',8,'Gurpreet Singh','gurpreet.s@example.com','+91 98550 56789',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-006','Diya','Banerjee',8,'Somnath Banerjee','somnath.b@example.com','+91 98660 67890',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-007','Aditya','Kulkarni',8,'Prakash Kulkarni','prakash.k@example.com','+91 98770 78901',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-008','Sneha','Reddy',9,'K. V. Reddy','kv.reddy@example.com','+91 98112 34567',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-009','Vivaan','Joshi',9,'Makarand Joshi','m.joshi@example.com','+91 98223 45678',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-010','Ishita','Deshmukh',9,'Sachin Deshmukh','sachin.d@example.com','+91 98334 56789',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-011','Reyansh','Gupta',9,'Alok Gupta','alok.gupta@example.com','+91 98445 67890',0,1,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-012','Tanvi','Nair',9,'Gopikrishnan Nair','gk.nair@example.com','+91 98556 78901',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-013','Aryan','Choudhury',6,'Pradip Choudhury','pradip.c@example.com','+91 98667 89012',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-014','Meera','Nambiar',6,'Ramesh Nambiar','ramesh.n@example.com','+91 98778 90123',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-015','Sai','Pranav',6,'Srinivas Rao','srinivas.r@example.com','+91 98889 01234',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-016','Avni','Malhotra',6,'Deepak Malhotra','deepak.m@example.com','+91 98990 12345',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-017','Harshvardhan','Rathore',6,'Vikram Singh Rathore','vikram.r@example.com','+91 98101 23456',1,1,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-018','Riya','Sen',7,'Debashis Sen','debashis.s@example.com','+91 98212 34567',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-019','Devansh','Tripathi',7,'Manoj Tripathi','manoj.t@example.com','+91 98323 45678',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-020','Khushi','Agarwal',7,'Pankaj Agarwal','pankaj.a@example.com','+91 98434 56789',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-021','Manav','Khatri',7,'Sanjay Khatri','sanjay.k@example.com','+91 98545 67890',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-022','Kavya','Menon',10,'K. R. Menon','kr.menon@example.com','+91 98656 78901',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-023','Arnav','Ghosh',10,'Subir Ghosh','subir.g@example.com','+91 98767 89012',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-024','Samaira','Kapoor',10,'Rohit Kapoor','rohit.k@example.com','+91 98878 90123',1,1,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-025','Siddharth','Pillai',10,'Murugan Pillai','murugan.p@example.com','+91 98989 01234',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-026','Tara','Bhatia',10,'Virender Bhatia','v.bhatia@example.com','+91 98190 12345',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-027','Yash','Chhabra',11,'Rajinder Chhabra','r.chhabra@example.com','+91 98201 23456',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-028','Nandini','Saxena',11,'Arun Saxena','arun.s@example.com','+91 98312 34567',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-029','Dhruv','Singhania',11,'Vijay Singhania','vijay.s@example.com','+91 98423 45678',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-030','Aniket','Bhardwaj',12,'Kuldeep Bhardwaj','k.bhardwaj@example.com','+91 98534 56789',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-031','Sanya','Mirza',12,'Farhan Mirza','farhan.m@example.com','+91 98645 67890',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-032','Pranav','Hegde',12,'Venkatesh Hegde','v.hegde@example.com','+91 98756 78901',1,1,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-033','Aanya','Pandey',5,'Sudhir Pandey','sudhir.p@example.com','+91 98867 89012',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-034','Atharva','Kadam',5,'Nitin Kadam','nitin.k@example.com','+91 98978 90123',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-035','Bhavya','Mishra',5,'Akhilesh Mishra','akhilesh.m@example.com','+91 98189 01234',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-036','Chirag','Dhar',3,'Anirban Dhar','anirban.d@example.com','+91 98290 12345',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-037','Disha','Goyal',3,'Naresh Goyal','naresh.g@example.com','+91 98301 23456',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-038','Eklavya','Rawat',4,'Surender Rawat','surender.r@example.com','+91 98412 34567',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-039','Gauri','Shukla',4,'Pramod Shukla','pramod.s@example.com','+91 98523 45678',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-040','Hridyansh','Bose',1,'Debashree Bose','debashree.b@example.com','+91 98634 56789',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-041','Ishani','Roy',1,'Sourav Roy','sourav.r@example.com','+91 98745 67890',0,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-042','Jayant','Chauhan',2,'Harpal Chauhan','harpal.c@example.com','+91 98856 78901',1,0,'ACTIVE','2026-11-04 17:46:33');
INSERT INTO "students" VALUES('ADM-2026-043','Kashvi','Sethi',2,'Varun Sethi','varun.s@example.com','+91 98967 89012',0,0,'ACTIVE','2026-11-04 17:46:33');
CREATE INDEX idx_students_class ON students(class_id);
CREATE INDEX idx_invoices_student ON invoices(student_id);
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_payments_invoice ON payments(invoice_id);
CREATE INDEX idx_receipts_payment ON receipts(payment_id);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('classes',12);
INSERT INTO "sqlite_sequence" VALUES('fee_heads',10);
INSERT INTO "sqlite_sequence" VALUES('discount_policies',6);
INSERT INTO "sqlite_sequence" VALUES('fee_structures',12);
INSERT INTO "sqlite_sequence" VALUES('fee_structure_items',103);
INSERT INTO "sqlite_sequence" VALUES('student_discounts',14);
INSERT INTO "sqlite_sequence" VALUES('invoices',35);
INSERT INTO "sqlite_sequence" VALUES('invoice_items',268);
INSERT INTO "sqlite_sequence" VALUES('audit_logs',50);
INSERT INTO "sqlite_sequence" VALUES('payments',15);
INSERT INTO "sqlite_sequence" VALUES('receipts',15);
COMMIT;
