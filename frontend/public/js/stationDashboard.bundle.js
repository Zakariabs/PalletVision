(()=>{var t=new URLSearchParams(window.location.search).get("station_id");console.log("Station ID:",t),t?(console.log("Fetching station details for ID:",t),function(t){fetch("http://127.0.0.1:5000/api/stations/".concat(t)).then((function(t){if(!t.ok)throw new Error("Failed to fetch station details");return t.json()})).then((function(t){var e=document.getElementById("station-name"),n=document.getElementById("station-info"),a=document.getElementById("station-status"),o=a.querySelector(".status-indicator");e.textContent=t.station_name,o.textContent=t.station_status,a.className="status-box p-3 rounded text-white ".concat(t.status_class),n.style.display="flex",o.style.display="inline"})).catch((function(t){return console.error("Error fetching station details:",t)}))}(t),function(t){fetch("http://127.0.0.1:5000/api/stations/".concat(t,"/inference_requests")).then((function(t){if(!t.ok)throw new Error("Failed to fetch inference requests");return t.json()})).then((function(t){!function(t){var e=document.getElementById("inference-requests");e.innerHTML="",t.forEach((function(t){var n="\n            <tr>\n                <td>".concat(new Date(t.answer_time).toLocaleString(),"</td>\n                <td>").concat(t.pallet_type,"</td>\n                <td>\n                    ").concat(t.initial_image_path?'<img src="'.concat(t.initial_image_path.replace("/app/app/ai_service/images/","http://localhost:5000/images/"),'" alt="Initial Image" class="table-image">'):'<span class="text-muted">No Image</span>',"\n                </td>\n                <td>\n                    ").concat(t.inferred_image_path?'<img src="'.concat(t.inferred_image_path.replace("/app/app/ai_service/","http://localhost:5000/images/"),'" alt="Inferred Image" class="table-image">'):'<span class="text-muted">No Image</span>',"\n                </td>\n                <td>").concat((100*t.confidence_level).toFixed(2),"%</td>\n            </tr>\n        ");e.insertAdjacentHTML("beforeend",n)}))}(t)})).catch((function(t){return console.error("Error fetching inference requests:",t)}))}(t)):console.error("No station_id provided in the URL")})();