using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.Collections.Generic;
using System.Linq;

namespace ActiveDirectoryUserReport.Tests
{
    [TestClass]
    public class ReportGeneratorTests
    {
        [TestMethod]
        public void GetUsers_WithMockServiceAndEnabledOnly_ReturnsOnlyEnabledUsers()
        {
            // Arrange
            IADService mockService = new MockADService();
            bool enabledOnly = true;
            var showProperties = new List<string> { "mail" };

            // Act
            var (reportData, headers) = mockService.GetUsers(null, enabledOnly, showProperties, false);

            // Assert
            Assert.AreEqual(1, reportData.Count, "Should return only one user because only one is enabled in the mock data.");
            Assert.AreEqual("jdoe", reportData[0]["sAMAccountName"]);
            Assert.IsTrue(headers.Contains("mail"));
        }

        [TestMethod]
        public void GetUsers_WithMockServiceAndShowProperties_ReturnsAllUsersWithExtraProperties()
        {
            // Arrange
            IADService mockService = new MockADService();
            bool enabledOnly = false;
            var showProperties = new List<string> { "mail", "description" };

            // Act
            var (reportData, headers) = mockService.GetUsers(null, enabledOnly, showProperties, false);

            // Assert
            Assert.AreEqual(2, reportData.Count, "Should return all users from mock data.");
            Assert.IsTrue(headers.Contains("mail"));
            Assert.IsTrue(headers.Contains("description"));

            var jdoe = reportData.First(u => u["sAMAccountName"] == "jdoe");
            var asmith = reportData.First(u => u["sAMAccountName"] == "asmith");

            Assert.AreEqual("[REDACTED]", jdoe["mail"]);
            Assert.AreEqual("N/A", jdoe["description"]); // jdoe doesn't have a description

            Assert.AreEqual("[REDACTED]", asmith["mail"]);
            Assert.AreEqual("Contractor", asmith["description"]);
        }
    }
}
