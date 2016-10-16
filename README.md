# Weathredds: A tool for collaborative weather forecasting

## Theory of operation

   Weathredds permits a meteorologist to create discussions about elements of a weather forecast. These discussions are arranged in **threads**. A thread has a title and a valid date/time which is shared among all the discussions in it. The intended use of a thread is to be able to track meteorologists' thinking as the forecast changes, e.g., as model solutions of a feature change over time. The addition of discussions to an existing thread is termed **extension**. The final discussion in a thread would likely be an examination of what conditions verified when the forecast time was reached.

   **Events** group together related threads. An event may contain any number of threads. An event can be labeled as *private* by the user that creates it. Unless an event is private, other users can view its associated threads, add to those threads, or create additional threads therein. A non-private event is termed *public*. A user can choose to specify a start and end date for an event, or they can allow it to *float* and let its timeframe be represented by the threads associated with it.

   One of the intended purposes of creating an event is to allow meteorologists to later go back and examine what was known (or believed) about that event before it happened. A possible application would be in examining what forecast techniques worked well in the past, when a similar event occurs again. For this reason an event may be assigned **tags**, which are basically identical in operation to those on blog and photo-sharing platforms. The intent is for all events matching a certain tag to be easily recalled later on down the road.

   A thread does not have an explicit owner, but rather a *steward* who is recongized as having initiated it. A steward can choose to *freeze* a thread to prevent other users from extending it--though this, by itself, does not prevent other users from reading it. If a thread's steward associates it with a public event, then the thread too becomes publicly viewable. Otherwise only the steward can see it.
   
   In summary, a user may choose to keep their content private by keeping events private and by associating threads only with those events, or leaving them unassociated altogether. However, it is intended that Weathredds facilitate situational awareness among all users.

   Events can be **pinned** to a user's main page for quick access. Pins are a convenience for ongoing events that a user is actively participating in. Only a user's own events, or others' public events, can be pinned.


## Future

* Timeline display: represent "everything going on" during a given time period
* Addition of images ("charts") to events, with thread-like capabilities for tracking changes
* Automatic database maintenance: removal of events not marked for archive, and threads not associated with such an event
* Review of events by month, season, year
