-- Master table for all HR documents (common + employee-specific)
CREATE TABLE HRDocuments (
    DocumentID INT IDENTITY(1,1) PRIMARY KEY,
    Title NVARCHAR(255) NOT NULL,
    FilePath NVARCHAR(MAX) NOT NULL,
    DocumentType NVARCHAR(100) NOT NULL, -- 'Handbook', 'Policy', 'OfferLetter', etc.
    UploadedBy INT NOT NULL,             -- HR employee ID
    CreatedAt DATETIME DEFAULT GETUTCDATE(),
    IsCommonDocument BIT DEFAULT 1       -- 1=Visible to all, 0=Employee-specific
);

-- Employee-specific document mappings
CREATE TABLE EmployeeDocuments (
    EmployeeDocumentID INT IDENTITY(1,1) PRIMARY KEY,
    EmployeeID INT NOT NULL,
    DocumentID INT NOT NULL,             -- FK to HRDocuments
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID),
    FOREIGN KEY (DocumentID) REFERENCES HRDocuments(DocumentID)
);

-- Insert common documents
INSERT INTO HRDocuments (Title, FilePath, DocumentType, UploadedBy, IsCommonDocument)
VALUES 
('Diversity & Inclusion Guidelines', 'https://drive.google.com/file/d/1T3iAkn_0FjZH7Mvceo1WXiMSZdB33kAH/view?usp=sharing', 'Policy', 101, 1),
('Official Employment Handbook', 'https://drive.google.com/file/d/1gX7i9FZ9C8-RnD7qKtUEuI4uWxwhln9Z/view?usp=sharing', 'Handbook', 101, 1);

-- Insert employee-specific offer letter
DECLARE @NewDocID INT;

INSERT INTO HRDocuments (Title, FilePath, DocumentType, UploadedBy, IsCommonDocument)
VALUES 
('Offer Letter - John Smith', 'https://drive.google.com/file/d/1h_bAofTDfy0iWw3HVZ9Wqp9LBqp2HHm9/view?usp=sharing', 'OfferLetter', 101, 0);

SET @NewDocID = SCOPE_IDENTITY();

-- Map offer letter to the employee
INSERT INTO EmployeeDocuments (EmployeeID, DocumentID)
VALUES (123, @NewDocID);


-- For common documents
INSERT INTO HRDocuments (Title, FilePath, DocumentType, UploadedBy, IsCommonDocument)
VALUES 
('Diversity & Inclusion', 'https://drive.google.com/.../Diversity_Inclusion.pdf', 'Policy', 101, 1),
('Employee Handbook', 'https://drive.google.com/.../Employment_Handbook.pdf', 'Handbook', 101, 1);

-- For employee-specific offer letters
INSERT INTO HRDocuments (Title, FilePath, DocumentType, UploadedBy, IsCommonDocument)
VALUES 
('Offer Letter - E123', 'https://drive.google.com/.../123_offer_letter.pdf', 'OfferLetter', 101, 0);

INSERT INTO EmployeeDocuments (EmployeeID, DocumentID)
VALUES (123, SCOPE_IDENTITY()); -- Link to last inserted ID


