using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

public class SumoReceiver : MonoBehaviour
{
    private TcpListener tcpListener;
    private Thread listenerThread;

    public readonly Dictionary<string, VehicleData> liveVehicles = new();
    public readonly object vehicleLock = new();

    void Start()
    {
        listenerThread = new Thread(new ThreadStart(ListenForMessages));
        listenerThread.IsBackground = true;
        listenerThread.Start();
    }

    void ListenForMessages()
    {
        tcpListener = new TcpListener(IPAddress.Parse("127.0.0.1"), 5005);
        tcpListener.Start();
        Debug.Log("TCP Listener started on port 5005");

        while (true)
        {
            using (TcpClient client = tcpListener.AcceptTcpClient())
            using (NetworkStream stream = client.GetStream())
            {
                byte[] buffer = new byte[8192];
                int length;

                while ((length = stream.Read(buffer, 0, buffer.Length)) != 0)
                {
                    string json = Encoding.UTF8.GetString(buffer, 0, length);

                    try
                    {
                        VehicleData[] vehicles = JsonHelper.FromJson<VehicleData>(json);
                        lock (vehicleLock)
                        {
                            liveVehicles.Clear();
                            foreach (var v in vehicles)
                            {
                                liveVehicles[v.id] = v;
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        Debug.LogError($"[TCP] Deserialization failed: {ex.Message}");
                    }
                }
            }
        }
    }

    // void Update()
    // {
    //     lock (vehicleLock)
    //     {
    //         if (liveVehicles.Count > 0)
    //         {
    //             StringBuilder sb = new();
    //             sb.AppendLine("[TCP] Vehicles Received This Step:");
    //             foreach (var v in liveVehicles.Values)
    //             {
    //                 sb.AppendLine($" - {v.id}: Pos=({v.x:F1},{v.y:F1}) Angle={v.angle:F1} Speed={v.speed:F1} " +
    //                               $"CO2={v.CO2:F1} Priority={v.priority} CO={v.CO:F1} HC={v.HC:F1} " +
    //                               $"NOx={v.NOx:F1} PMx={v.PMx:F1} Fuel={v.fuel:F1} Electricity={v.electricity:F1} ");
    //             }
    //             Debug.Log(sb.ToString());
    //         }
    //     }
    // }

    void OnApplicationQuit()
    {
        tcpListener.Stop();
    }
}

[Serializable]
public class VehicleData
{
    public string id;
    public float x, y, angle, speed;
    public float CO2, CO, HC, NOx, PMx;
    public float fuel, electricity, noise, priority;
}
public static class JsonHelper
{
    public static T[] FromJson<T>(string json)
    {
        Wrapper<T> wrapper = JsonUtility.FromJson<Wrapper<T>>(WrapJson(json));
        return wrapper.Items;
    }

    private static string WrapJson(string json)
    {
        return "{\"Items\":" + json + "}";
    }

    [Serializable]
    private class Wrapper<T>
    {
        public T[] Items;
    }
}