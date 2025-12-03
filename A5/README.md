# A5 - REFLECTION

## My learning experience:

- Identification of my own level at the beginning of this course and where I ended

At the start of this course, I would classify myself as operating between a **modeler** and **analyst** level. I had prior experience from the OpenBIM course where I modeled a building, and I possessed some Python knowledge that enabled me to analyze data through scripts. Together with my group members, I initially took on the **manager** role. However, both group members dropped out after the second lesson, leaving me at a crossroads. I considered stepping down from the OpenBIM manager responsibility but ultimately decided to continue. I saw this as an opportunity for personal development—to simultaneously analyze data while managing coordination between other groups, gathering their knowledge, and elevating scripts based on their collective analyses. Through this journey, I evolved from a modeler/analyst into a relatively confident **OpenBIM manager**, capable of handling both technical analysis and project coordination responsibilities.

- What else do I still need to learn?

I still need to learn more about the mechanisms in OpenBIM through IFC files and how BlenderBIM/Bonsai works 100% to feel completely confident within the subject. I also need to dive deeper into how Python operates through ifcopenshell to understand the root of the information being extracted from the model/IFC file. I would love to learn more about how to implement coding and automation of workflows in e.g., Revit (even though I know that Autodesk is not well-regarded in this course :-D)

- How I might use OpenBIM in the future

I would really like to use OpenBIM at my workplace as a building designer to automate some processes that normally take a long time to complete. This applies to both modeling but also documentation of projects that could be automated and made smarter through OpenBIM. I would also like to introduce the use of open file formats like IFC instead of Revit at my workplace so everyone could have access to the building model and extract information about it without necessarily having access to Revit or similar software.

- Did the process of the course enable me to answer or define questions that I might need later for my thesis?

I am currently writing my diploma project and will not be using the content from this course as I am writing my project concurrently with this course. But for later projects, the same process could be implemented if the opportunity and necessity arise.

- Would I have preferred to have been given less choice in the use cases?

No. I liked that it was an open field where you could use your own knowledge to find a case that would be relevant to yourself. This way, everything becomes more individualized and nuanced than if the possibilities were more limited.

- Was the number of tools for the course ok - should we have more or less? - if so which ones would I leave out?

I think the number of tools was very appropriate as there were many different disciplines that could embrace these in their own way.

- Note

I did not develop a tutorial for my script but rather a tutorial for something I thought was relevant for everyone taking on the role as OpenBIM manager and possibly also for OpenBIM analysts -> see assignment A4

## Summary of the feedback I received on my tutorial

- Did the tool address the use case I identified?

### Script feedback

My script did almost what I wanted it to but failed to connect the two analyst scripts 100% together. Since the results from the two scripts differentiated from each other, it was difficult to find direct connections between the two. I was therefore forced to assume that the rooms that had a door from one script had access to the corridor that the other group had identified. Requirements for building regulations were complied with and analyzed as expected. General feedback on all the scripts from the architects was:

1. Generally, we work mostly with geometry and the connections between geometries are difficult to find as they are not specified anywhere when creating the model
2. Doors are a general problem as we don't know if it's an internal wall to a toilet or to a corridor, which was part of the goal to figure out.
3. The tools became very specific and not as universal as they are based both on names and types and not only types which are global and not just individual for each model you work with.
4. I couldn't consolidate data between the two scripts as their common connection (the door) was not defined the same way in each script. To solve this, it needs to be built up in the same way to be able to identify when a door belongs to a room with desks and leads out to the escape route.

### Tutorial feedback

My presentation consisted of a presentation of my tutorial on GitHub for managers and possibly also helpful for analysts. I received no questions but got good recognition with a show of hands that it could have been helpful for many of my fellow students, which was the ultimate goal of the tutorial.

- What stage does the tool I created work in Advanced Building Design? ( Stage A, B, C and/ or D).

As described in assignment A3, my tool can be used in both design phase C and D depending on how you want to implement it. "This tool is particularly useful in **Stage C** of the Advanced Building Design process, where the arrangement of spaces and furniture is finalized. It could also be helpful in **Stage D**, where details and optimization are applied to the design process to ensure that desk locations comply with accessibility requirements." quote from A3

## My Future Vision for Advanced OpenBIM Applications

- Am I likely to use OpenBIM tools in my thesis?

Since I am writing my diploma project concurrently with the course, I have not had the opportunity to implement it. If I one day choose to pursue a master's degree and have to write a master's thesis, I would like to implement some of the tools I have learned in this course.

- Am I likely to use OpenBIM tools in my professsional life in the next 10 years?

Yes, if the means and openness for using OpenBIM at my future workplace are there, I would really like to try to get it implemented.

## Conclusion: My Journey Through A1-A5

My journey through this course began with **A1**, where I entered with previous experience as an OpenBIM modeler and analyst, but not as a manager. Taking on the manager role proved successful as I worked on my own analysis while simultaneously gathering and coordinating various analyses from the architect groups.

This foundation led naturally into **A2**, where I gained new experience creating BPMN diagrams. This assignment provided valuable insight into how to effectively present and visualize how a script works, including its purpose, inputs, and outputs—skills that would prove essential for the collaborative work ahead.

**A3** presented significant challenges, as I faced limitations at the start due to my dependency on other groups' scripts. My goal was to create a master script that would summarize all information and establish the connection between desk accessibility and escape routes in the building. While working through these technical obstacles, I simultaneously developed my tutorial for A4, which took a different direction from my script work. Despite the challenges, I completed the script and came close to achieving the desired result defined in A2, though it pushed my capabilities considerably.

The struggles I encountered throughout the course, particularly with GitHub and the manager workflow, inspired **A4**. Keeping track of all scripts, ensuring they functioned correctly, and maintaining proper access to analyst materials proved challenging. These experiences made it clear that my tutorial should focus on GitHub and the workflow between Visual Studio Code and GitHub. I believed this would have benefited me greatly at the beginning, and I hoped it could help future students facing similar challenges.

Finally, **A5** has provided valuable insight into my entire journey through the course, helping me reflect on where I should have placed more focus. The assignments connected well together, and I managed to maintain a coherent thread throughout that forms the basis for my learning and achievements in this course.
