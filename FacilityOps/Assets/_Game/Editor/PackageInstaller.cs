using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;

namespace FacilityOps.Editor
{
    public static class PackageInstaller
    {
        private static AddRequest request;
        private static double deadline;
        public static void Install()
        {
            request = Client.Add("com.unity.modules.screencapture@1.0.0");
            deadline = EditorApplication.timeSinceStartup + 180;
            EditorApplication.update += Poll;
        }
        private static void Poll()
        {
            if (!request.IsCompleted && EditorApplication.timeSinceStartup < deadline) return;
            EditorApplication.update -= Poll;
            bool success = request.IsCompleted && request.Status == StatusCode.Success;
            Debug.Log(success ? "SCREEN CAPTURE PACKAGE INSTALLED" : "PACKAGE FAILED: " + request.Error?.message);
            EditorApplication.Exit(success ? 0 : 1);
        }
    }
}
