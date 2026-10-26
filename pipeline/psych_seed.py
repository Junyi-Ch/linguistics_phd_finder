"""Builds data/psych/programs.json: U.S. News 2027 National Universities top 100 (ties at 100 -> 108 schools).

Unit tuple: (name, type, homepage, home, include, note)
  type: PSY (psychology or its equivalent), COGSCI, NEURO (a department or program named neuroscience)
  home: main = main campus arts & sciences; mixed = program with main-campus and medical-school faculty;
        med = run from the medical school
  include: False for units that are left out (clinical, education school, neurobiology, medical school, no PhD)
Scope rule: keep people whose research is relevant to psychology; leave out clinical psychology,
education-school psychology, neurobiology departments and medical schools.
"""
import json, re, sys

V = "verify"
U = [
 (1, "Massachusetts Institute of Technology", [
   ("Department of Brain and Cognitive Sciences", "PSY", "https://bcs.mit.edu/", "main", True, "MIT's psychology department; covers cognitive science and neuroscience")]),
 (2, "Princeton University", [
   ("Department of Psychology", "PSY", "https://psychology.princeton.edu/", "main", True, ""),
   ("Princeton Neuroscience Institute", "NEURO", "https://pni.princeton.edu/", "main", True, "")]),
 (3, "Harvard University", [
   ("Department of Psychology", "PSY", "https://psychology.fas.harvard.edu/", "main", True, ""),
   ("Program in Neuroscience", "NEURO", "https://pinphd.hms.harvard.edu/", "med", False, "run by Harvard Medical School")]),
 (4, "Yale University", [
   ("Department of Psychology", "PSY", "https://psychology.yale.edu/", "main", True, ""),
   ("Interdepartmental Neuroscience Program", "NEURO", "https://medicine.yale.edu/inp/", "mixed", True, "mostly School of Medicine; keep psychology-relevant main-campus people")]),
 (5, "California Institute of Technology", [
   ("Computation and Neural Systems", "NEURO", "https://www.cns.caltech.edu/", "main", True, "no psychology department at Caltech"),
   ("Social and Decision Neuroscience", "NEURO", "https://www.hss.caltech.edu/graduate-studies/social-and-decision-neuroscience", "main", True, ""),
   ("Neurobiology (Biology and Biological Engineering)", "NEURO", "https://www.bbe.caltech.edu/", "main", False, "neurobiology")]),
 (5, "Stanford University", [
   ("Department of Psychology", "PSY", "https://psychology.stanford.edu/", "main", True, ""),
   ("Neurosciences PhD Program", "NEURO", "https://med.stanford.edu/neurogradprogram.html", "mixed", True, "run from the School of Medicine; keep psychology-relevant main-campus people"),
   ("Graduate School of Education (developmental and psychological sciences)", "PSY", "https://ed.stanford.edu/", "main", False, "education school")]),
 (7, "University of Pennsylvania", [
   ("Department of Psychology", "PSY", "https://psychology.sas.upenn.edu/", "main", True, ""),
   ("Neuroscience Graduate Group", "NEURO", "https://www.med.upenn.edu/ngg/", "mixed", True, "mostly Perelman School of Medicine; keep psychology-relevant people")]),
 (8, "Duke University", [
   ("Department of Psychology and Neuroscience", "PSY", "https://psychandneuro.duke.edu/", "main", True, ""),
   ("Department of Neurobiology", "NEURO", "https://www.neuro.duke.edu/", "med", False, "neurobiology, School of Medicine")]),
 (9, "Johns Hopkins University", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://pbs.jhu.edu/", "main", True, ""),
   ("Department of Cognitive Science", "COGSCI", "https://cogsci.jhu.edu/", "main", True, ""),
   ("Neuroscience Graduate Program", "NEURO", "https://neuroscience.jhu.edu/", "med", False, "School of Medicine")]),
 (9, "Northwestern University", [
   ("Department of Psychology", "PSY", "https://psychology.northwestern.edu/", "main", True, ""),
   ("Northwestern University Interdepartmental Neuroscience (NUIN)", "NEURO", "https://www.nuin.northwestern.edu/", "mixed", True, "Evanston and Feinberg; keep psychology-relevant people")]),
 (9, "University of Chicago", [
   ("Department of Psychology", "PSY", "https://psychology.uchicago.edu/", "main", True, ""),
   ("Committee on Computational Neuroscience", "NEURO", "https://neuroscience.uchicago.edu/", "mixed", True, "Biological Sciences Division; keep psychology-relevant people"),
   ("Comparative Human Development", "PSY", "https://chd.uchicago.edu/", "main", True, "psychology-heavy interdisciplinary department")]),
 (12, "Columbia University", [
   ("Department of Psychology", "PSY", "https://psychology.columbia.edu/", "main", True, ""),
   ("Neurobiology and Behavior (Zuckerman Institute)", "NEURO", "https://neurosciencephd.columbia.edu/", "mixed", True, "doctoral program in neurobiology and behavior; keep psychology-relevant people"),
   ("Teachers College (Human Development, Clinical)", "PSY", "https://www.tc.columbia.edu/", "main", False, "education school")]),
 (12, "Dartmouth College", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://pbs.dartmouth.edu/", "main", True, "")]),
 (14, "Carnegie Mellon University", [
   ("Department of Psychology", "PSY", "https://www.cmu.edu/dietrich/psychology/", "main", True, ""),
   ("Neuroscience Institute", "NEURO", "https://www.cmu.edu/ni/", "main", True, "")]),
 (14, "Cornell University", [
   ("Department of Psychology", "PSY", "https://psychology.cornell.edu/", "main", True, ""),
   ("Department of Psychology (College of Human Ecology; formerly Human Development)", "PSY", "https://www.human.cornell.edu/psych", "main", True, "Cornell's second psychology department"),
   ("Neurobiology and Behavior", "NEURO", "https://nbb.cornell.edu/", "main", False, "neurobiology")]),
 (16, "Brown University", [
   ("Cognitive and Psychological Sciences (CLPS)", "PSY", "https://cogsci.brown.edu/", "main", True, ""),
   ("Department of Neuroscience", "NEURO", "https://www.brown.edu/academics/neuroscience/", "main", True, "")]),
 (16, "Rice University", [
   ("Department of Psychological Sciences", "PSY", "https://psychology.rice.edu/", "main", True, "")]),
 (16, "Vanderbilt University", [
   ("Department of Psychology (College of Arts and Science)", "PSY", "https://www.vanderbilt.edu/psychological_sciences/", "main", True, ""),
   ("Vanderbilt Brain Institute neuroscience PhD", "NEURO", "https://www.vanderbilt.edu/brain-institute/", "mixed", True, "keep psychology-relevant people"),
   ("Psychology and Human Development (Peabody College)", "PSY", "https://peabody.vanderbilt.edu/departments/psych/", "main", False, "education school")]),
 (16, "Washington University in St. Louis", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://psych.wustl.edu/", "main", True, ""),
   ("Neurosciences PhD (DBBS)", "NEURO", "https://dbbs.wustl.edu/programs/neuroscience/", "med", False, "School of Medicine")]),
 (20, "University of California, Berkeley", [
   ("Department of Psychology", "PSY", "https://psychology.berkeley.edu/", "main", True, ""),
   ("Helen Wills Neuroscience Institute", "NEURO", "https://neuroscience.berkeley.edu/", "main", True, ""),
   ("Graduate School of Education (human development)", "PSY", "https://bse.berkeley.edu/", "main", False, "education school")]),
 (20, "University of California, Los Angeles", [
   ("Department of Psychology", "PSY", "https://www.psych.ucla.edu/", "main", True, ""),
   ("Neuroscience Interdepartmental PhD Program", "NEURO", "https://www.neuroscience.ucla.edu/", "mixed", True, "keep psychology-relevant people")]),
 (20, "University of Notre Dame", [
   ("Department of Psychology", "PSY", "https://psychology.nd.edu/", "main", True, "")]),
 (23, "Emory University", [
   ("Department of Psychology", "PSY", "https://psychology.emory.edu/", "main", True, ""),
   ("Neuroscience PhD (Laney Graduate School)", "NEURO", "https://biomed.emory.edu/program/neuroscience/", "mixed", True, "keep psychology-relevant people")]),
 (23, "Georgetown University", [
   ("Department of Psychology", "PSY", "https://psychology.georgetown.edu/", "main", True, ""),
   ("Interdisciplinary Program in Neuroscience", "NEURO", "https://neuroscience.georgetown.edu/", "mixed", True, "Medical Center campus; keep psychology-relevant people")]),
 (25, "University of Michigan–Ann Arbor", [
   ("Department of Psychology", "PSY", "https://lsa.umich.edu/psych", "main", True, ""),
   ("Neuroscience Graduate Program", "NEURO", "https://medicine.umich.edu/medschool/education/phd-programs/neuroscience-graduate-program", "mixed", True, "keep psychology-relevant people"),
   ("Combined Program in Education and Psychology", "PSY", "https://soe.umich.edu/", "main", False, "education school")]),
 (26, "University of Virginia", [
   ("Department of Psychology", "PSY", "https://psychology.as.virginia.edu/", "main", True, ""),
   ("Neuroscience Graduate Program", "NEURO", "https://med.virginia.edu/neuroscience-graduate-program/", "mixed", True, "keep psychology-relevant people")]),
 (27, "University of North Carolina–Chapel Hill", [
   ("Department of Psychology and Neuroscience", "PSY", "https://psychology.unc.edu/", "main", True, ""),
   ("Neuroscience Curriculum", "NEURO", "https://www.med.unc.edu/neuroscience/", "med", False, "School of Medicine")]),
 (27, "University of Southern California", [
   ("Department of Psychology", "PSY", "https://dornsife.usc.edu/psyc/", "main", True, ""),
   ("Neuroscience Graduate Program", "NEURO", "https://ngp.usc.edu/", "mixed", True, "keep psychology-relevant people")]),
 (29, "Georgia Institute of Technology", [
   ("School of Psychology", "PSY", "https://psychology.gatech.edu/", "main", True, ""),
   ("Neuroscience and Neurotechnology PhD", "NEURO", "https://neuroscience.cos.gatech.edu/", "main", True, "")]),
 (29, "University of California San Diego", [
   ("Department of Psychology", "PSY", "https://psychology.ucsd.edu/", "main", True, ""),
   ("Department of Cognitive Science", "COGSCI", "https://cogsci.ucsd.edu/", "main", True, ""),
   ("Neurosciences Graduate Program", "NEURO", "https://neurograd.ucsd.edu/", "mixed", True, "keep psychology-relevant people")]),
 (31, "Boston College", [
   ("Department of Psychology and Neuroscience", "PSY", "https://www.bc.edu/bc-web/schools/morrissey/departments/psychology.html", "main", True, "")]),
 (31, "New York University", [
   ("Department of Psychology", "PSY", "https://psychology.as.nyu.edu/", "main", True, ""),
   ("Center for Neural Science", "NEURO", "https://as.nyu.edu/departments/cns.html", "main", True, ""),
   ("Applied Psychology (Steinhardt)", "PSY", "https://steinhardt.nyu.edu/appsych", "main", False, "education school")]),
 (31, "Tufts University", [
   ("Department of Psychology", "PSY", "https://as.tufts.edu/psychology/", "main", True, ""),
   ("Neuroscience PhD (Graduate School of Biomedical Sciences)", "NEURO", "https://gsbs.tufts.edu/academics/neuroscience", "med", False, "medical campus")]),
 (34, "Boston University", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://www.bu.edu/psych/", "main", True, ""),
   ("Graduate Program for Neuroscience", "NEURO", "https://www.bu.edu/neuro/", "mixed", True, "keep psychology-relevant people")]),
 (34, "University of California, Davis", [
   ("Department of Psychology", "PSY", "https://psychology.ucdavis.edu/", "main", True, ""),
   ("Center for Neuroscience / Neuroscience Graduate Group", "NEURO", "https://neuroscience.ucdavis.edu/", "mixed", True, "keep psychology-relevant people"),
   ("Human Development Graduate Group", "PSY", "https://hdgg.ucdavis.edu/", "main", True, "developmental psychology heavy; included")]),
 (34, "University of California, Irvine", [
   ("Department of Cognitive Sciences", "COGSCI", "https://www.cogsci.uci.edu/", "main", True, ""),
   ("Department of Psychological Science", "PSY", "https://psychology.uci.edu/", "main", True, ""),
   ("Interdepartmental Neuroscience Program", "NEURO", "https://inp.uci.edu/", "mixed", True, "keep psychology-relevant people"),
   ("Neurobiology and Behavior", "NEURO", "https://nb.bio.uci.edu/", "main", False, "neurobiology")]),
 (34, "University of Florida", [
   ("Department of Psychology", "PSY", "https://psych.ufl.edu/", "main", True, ""),
   ("Clinical and Health Psychology", "PSY", "https://chp.phhp.ufl.edu/", "med", False, "clinical")]),
 (34, "University of Illinois Urbana-Champaign", [
   ("Department of Psychology", "PSY", "https://psychology.illinois.edu/", "main", True, ""),
   ("Neuroscience Program", "NEURO", "https://neuroscience.illinois.edu/", "main", True, "")]),
 (34, "University of Texas–Austin", [
   ("Department of Psychology", "PSY", "https://liberalarts.utexas.edu/psychology/", "main", True, ""),
   ("Department of Neuroscience", "NEURO", "https://neuroscience.utexas.edu/", "main", True, ""),
   ("Educational Psychology", "PSY", "https://education.utexas.edu/departments/educational-psychology/", "main", False, "education school")]),
 (34, "University of Wisconsin–Madison", [
   ("Department of Psychology", "PSY", "https://psych.wisc.edu/", "main", True, ""),
   ("Neuroscience Training Program", "NEURO", "https://ntp.neuroscience.wisc.edu/", "mixed", True, "keep psychology-relevant people"),
   ("Educational Psychology", "PSY", "https://edpsych.education.wisc.edu/", "main", False, "education school")]),
 (34, "Wake Forest University", [
   ("Department of Psychology", "PSY", "https://psychology.wfu.edu/", "main", False, "master's only, no PhD"),
   ("Neuroscience PhD", "NEURO", "https://school.wakehealth.edu/education-and-training/graduate-programs/neuroscience", "med", False, "School of Medicine")]),
 (42, "Northeastern University", [
   ("Department of Psychology", "PSY", "https://cos.northeastern.edu/psychology/", "main", True, "")]),
 (42, "Villanova University", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://www1.villanova.edu/university/liberal-arts-sciences/programs/psychology.html", "main", False, "master's only, no PhD")]),
 (44, "Case Western Reserve University", [
   ("Department of Psychological Sciences", "PSY", "https://case.edu/artsci/psych/", "main", True, ""),
   ("Department of Cognitive Science", "COGSCI", "https://case.edu/artsci/cogsci/", "main", True, ""),
   ("Department of Neurosciences", "NEURO", "https://case.edu/medicine/neurosciences/", "med", False, "School of Medicine")]),
 (44, "Lehigh University", [
   ("Department of Psychology", "PSY", "https://psychology.cas.lehigh.edu/", "main", True, "")]),
 (44, "The Ohio State University", [
   ("Department of Psychology", "PSY", "https://psychology.osu.edu/", "main", True, ""),
   ("Neuroscience Graduate Program", "NEURO", "https://ngp.osu.edu/", "mixed", True, "keep psychology-relevant people")]),
 (44, "Rutgers University–New Brunswick", [
   ("Department of Psychology", "PSY", "https://psych.rutgers.edu/", "main", True, ""),
   ("Rutgers Center for Cognitive Science", "COGSCI", "https://ruccs.rutgers.edu/", "main", True, ""),
   ("Neuroscience Graduate Program (Brain Health Institute)", "NEURO", "https://bhi.rutgers.edu/", "mixed", True, "keep psychology-relevant people"),
   ("GSAPP (clinical and school psychology)", "PSY", "https://gsapp.rutgers.edu/", "main", False, "clinical")]),
 (44, "University of California, Santa Barbara", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://www.psych.ucsb.edu/", "main", True, ""),
   ("Dynamical Neuroscience PhD", "NEURO", "https://www.dyns.ucsb.edu/", "main", True, ""),
   ("Counseling, Clinical and School Psychology", "PSY", "https://ccsp.education.ucsb.edu/", "main", False, "education school, clinical")]),
 (49, "University of Maryland, College Park", [
   ("Department of Psychology", "PSY", "https://psyc.umd.edu/", "main", True, ""),
   ("Neuroscience and Cognitive Science Program (NACS)", "NEURO", "https://nacs.umd.edu/", "main", True, ""),
   ("Human Development and Quantitative Methodology", "PSY", "https://education.umd.edu/hdqm", "main", False, "education school")]),
 (49, "University of Rochester", [
   ("Department of Brain and Cognitive Sciences", "PSY", "https://www.sas.rochester.edu/bcs/", "main", True, ""),
   ("Department of Psychology", "PSY", "https://www.sas.rochester.edu/psy/", "main", True, ""),
   ("Neuroscience Graduate Program", "NEURO", "https://www.urmc.rochester.edu/neuroscience/", "med", False, "Medical Center")]),
 (49, "University of Washington", [
   ("Department of Psychology", "PSY", "https://psych.uw.edu/", "main", True, ""),
   ("Graduate Program in Neuroscience", "NEURO", "https://neuroscience.uw.edu/", "mixed", True, "keep psychology-relevant people")]),
 (52, "University of Georgia", [
   ("Department of Psychology", "PSY", "https://psychology.uga.edu/", "main", True, ""),
   ("Neuroscience PhD (Biomedical and Health Sciences Institute)", "NEURO", "https://neuroscience.uga.edu/", "main", True, "")]),
 (52, "Virginia Tech", [
   ("Department of Psychology", "PSY", "https://psyc.vt.edu/", "main", True, ""),
   ("School of Neuroscience", "NEURO", "https://neuroscience.vt.edu/", "main", True, "")]),
 (52, "William & Mary", [
   ("Department of Psychological Sciences", "PSY", "https://www.wm.edu/as/psychologicalsciences/", "main", False, "no research PhD")]),
 (55, "Pennsylvania State University–University Park", [
   ("Department of Psychology", "PSY", "https://psych.la.psu.edu/", "main", True, ""),
   ("Neuroscience Graduate Program", "NEURO", "https://neuroscience.psu.edu/", "mixed", True, "keep psychology-relevant people"),
   ("Human Development and Family Studies", "PSY", "https://hhd.psu.edu/hdfs", "main", True, "developmental psychology heavy; included")]),
 (55, "Purdue University–Main Campus", [
   ("Department of Psychological Sciences", "PSY", "https://www.purdue.edu/hhs/psy/", "main", True, ""),
   ("Purdue Institute for Integrative Neuroscience", "NEURO", "https://www.purdue.edu/research/institutes/integrative-neuroscience/", "main", True, "university neuroscience institute; keep psychology-relevant people")]),
 (55, "Santa Clara University", [
   ("Department of Psychology", "PSY", "https://www.scu.edu/cas/psychology/", "main", False, "no PhD")]),
 (55, "University of Miami", [
   ("Department of Psychology", "PSY", "https://psychology.as.miami.edu/", "main", True, ""),
   ("Neuroscience PhD", "NEURO", "https://med.miami.edu/programs/neuroscience-phd", "med", False, "Miller School of Medicine")]),
 (59, "Brandeis University", [
   ("Department of Psychology", "PSY", "https://www.brandeis.edu/psychology/", "main", True, ""),
   ("Neuroscience PhD", "NEURO", "https://www.brandeis.edu/neuroscience/", "main", True, "")]),
 (59, "Florida State University", [
   ("Department of Psychology", "PSY", "https://psy.fsu.edu/", "main", True, ""),
   ("Program in Neuroscience", "NEURO", "https://neuro.fsu.edu/", "mixed", True, "keep psychology-relevant people")]),
 (59, "George Washington University", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://psychology.columbian.gwu.edu/", "main", True, "")]),
 (59, "Stevens Institute of Technology", []),
 (59, "Stony Brook University–SUNY", [
   ("Department of Psychology", "PSY", "https://www.stonybrook.edu/commcms/psychology/", "main", True, ""),
   ("Neuroscience Graduate Program", "NEURO", "https://neuro.stonybrookmedicine.edu/", "med", False, "Renaissance School of Medicine")]),
 (59, "Texas A&M University", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://psychology.tamu.edu/", "main", True, ""),
   ("Texas A&M Institute for Neuroscience", "NEURO", "https://tamin.tamu.edu/", "mixed", True, "keep psychology-relevant people")]),
 (59, "Tulane University of Louisiana", [
   ("Department of Psychology", "PSY", "https://sse.tulane.edu/psychology", "main", True, ""),
   ("Neuroscience PhD (Brain Institute)", "NEURO", "https://brain.tulane.edu/", "main", True, "")]),
 (59, "University of Massachusetts–Amherst", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://www.umass.edu/pbs/", "main", True, ""),
   ("Neuroscience and Behavior Graduate Program", "NEURO", "https://www.umass.edu/neuro/", "main", True, "")]),
 (59, "University of Minnesota–Twin Cities", [
   ("Department of Psychology", "PSY", "https://cla.umn.edu/psychology", "main", True, ""),
   ("Graduate Program in Neuroscience", "NEURO", "https://med.umn.edu/neuroscience", "med", False, "Medical School"),
   ("Institute of Child Development", "PSY", "https://cehd.umn.edu/icd/", "main", False, "education school (CEHD)")]),
 (59, "University of Pittsburgh", [
   ("Department of Psychology", "PSY", "https://www.psychology.pitt.edu/", "main", True, ""),
   ("Department of Neuroscience", "NEURO", "https://www.neuroscience.pitt.edu/", "main", True, "")]),
 (69, "Michigan State University", [
   ("Department of Psychology", "PSY", "https://psychology.msu.edu/", "main", True, ""),
   ("Neuroscience Program", "NEURO", "https://neuroscience.msu.edu/", "mixed", True, "keep psychology-relevant people")]),
 (69, "Rensselaer Polytechnic Institute", [
   ("Department of Cognitive Science", "COGSCI", "https://cogsci.rpi.edu/", "main", True, "")]),
 (69, "University of California, Merced", [
   ("Department of Psychological Sciences", "PSY", "https://psychology.ucmerced.edu/", "main", True, ""),
   ("Department of Cognitive and Information Sciences", "COGSCI", "https://cogsci.ucmerced.edu/", "main", True, "")]),
 (72, "Syracuse University", [
   ("Department of Psychology", "PSY", "https://artsandsciences.syracuse.edu/psychology-department/", "main", True, "")]),
 (73, "Binghamton University–SUNY", [
   ("Department of Psychology", "PSY", "https://www.binghamton.edu/psychology/", "main", True, "")]),
 (73, "Howard University", [
   ("Department of Psychology", "PSY", "https://coas.howard.edu/psychology", "main", True, "")]),
 (73, "Indiana University–Bloomington", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://psych.indiana.edu/", "main", True, ""),
   ("Cognitive Science Program", "COGSCI", "https://cogs.indiana.edu/", "main", True, ""),
   ("Program in Neuroscience", "NEURO", "https://neuroscience.indiana.edu/", "main", True, "")]),
 (73, "North Carolina State University", [
   ("Department of Psychology", "PSY", "https://psychology.chass.ncsu.edu/", "main", True, "")]),
 (73, "Rutgers University–Newark", [
   ("Department of Psychology", "PSY", "https://sasn.rutgers.edu/academics-admissions/academic-departments/psychology", "main", True, ""),
   ("Center for Molecular and Behavioral Neuroscience", "NEURO", "https://cmbn.rutgers.edu/", "main", True, "")]),
 (73, "University of Connecticut", [
   ("Department of Psychological Sciences", "PSY", "https://psychology.uconn.edu/", "main", True, "")]),
 (73, "Worcester Polytechnic Institute", [
   ("Department of Psychological Science", "PSY", "https://www.wpi.edu/academics/departments/psychological-science", "main", True, "small department; included")]),
 (80, "Clemson University", [
   ("Department of Psychology", "PSY", "https://www.clemson.edu/cbshs/departments/psychology/", "main", True, "")]),
 (80, "Colorado School of Mines", []),
 (80, "Drexel University", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://drexel.edu/coas/academics/departments-centers/psychology/", "main", True, "")]),
 (80, "Pepperdine University", [
   ("Graduate School of Education and Psychology", "PSY", "https://gsep.pepperdine.edu/", "main", False, "education school, clinical PsyD only")]),
 (80, "University of California, Riverside", [
   ("Department of Psychology", "PSY", "https://psychology.ucr.edu/", "main", True, ""),
   ("Neuroscience Graduate Program", "NEURO", "https://neuroscience.ucr.edu/", "mixed", True, "keep psychology-relevant people")]),
 (85, "Fordham University", [
   ("Department of Psychology", "PSY", "https://www.fordham.edu/academics/departments/psychology/", "main", True, "")]),
 (85, "New Jersey Institute of Technology", []),
 (85, "Southern Methodist University", [
   ("Department of Psychology", "PSY", "https://www.smu.edu/dedman/academics/departments/psychology", "main", True, "")]),
 (85, "University at Buffalo–SUNY", [
   ("Department of Psychology", "PSY", "https://arts-sciences.buffalo.edu/psychology.html", "main", True, ""),
   ("Neuroscience Program", "NEURO", "https://medicine.buffalo.edu/departments/physiology_and_biophysics/education/neuroscience.html", "med", False, "Jacobs School of Medicine")]),
 (85, "University of Delaware", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://www.psych.udel.edu/", "main", True, "")]),
 (90, "Baylor University", [
   ("Department of Psychology and Neuroscience", "PSY", "https://psychologyneuroscience.artsandsciences.baylor.edu/", "main", True, "")]),
 (90, "Gonzaga University", []),
 (90, "Marquette University", [
   ("Department of Psychology", "PSY", "https://www.marquette.edu/psychology/", "main", False, "clinical PhD only")]),
 (90, "Texas Christian University", [
   ("Department of Psychology", "PSY", "https://psychology.tcu.edu/", "main", True, "")]),
 (90, "Yeshiva University", [
   ("Ferkauf Graduate School of Psychology", "PSY", "https://www.yu.edu/ferkauf", "main", False, "clinical and school psychology only")]),
 (95, "American University", [
   ("Department of Psychology", "PSY", "https://www.american.edu/cas/psychology/", "main", True, "")]),
 (95, "Rochester Institute of Technology", [
   ("Department of Psychology (Cognitive Science PhD)", "COGSCI", "https://www.rit.edu/liberalarts/department-psychology", "main", True, "")]),
 (95, "Rutgers University–Camden", [
   ("Department of Psychology", "PSY", "https://psychology.camden.rutgers.edu/", "main", False, "no psychology PhD")]),
 (95, "University of Illinois Chicago", [
   ("Department of Psychology", "PSY", "https://psch.uic.edu/", "main", True, ""),
   ("Graduate Program in Neuroscience", "NEURO", "https://neuroscience.uic.edu/", "mixed", True, "keep psychology-relevant people")]),
 (95, "University of Missouri", [
   ("Department of Psychological Sciences", "PSY", "https://psychology.missouri.edu/", "main", True, "")]),
 (100, "Auburn University", [
   ("Department of Psychological Sciences", "PSY", "https://cla.auburn.edu/psychology/", "main", True, "")]),
 (100, "Chapman University", [
   ("Department of Psychology (Crean College)", "PSY", "https://www.chapman.edu/crean/", "main", False, V + ": no psychology PhD found")]),
 (100, "Creighton University", []),
 (100, "Elon University", []),
 (100, "Florida International University", [
   ("Department of Psychology", "PSY", "https://psychology.fiu.edu/", "main", True, "")]),
 (100, "Saint Louis University", [
   ("Department of Psychology", "PSY", "https://www.slu.edu/arts-and-sciences/psychology/", "main", True, "")]),
 (100, "University of Iowa", [
   ("Department of Psychological and Brain Sciences", "PSY", "https://psychology.uiowa.edu/", "main", True, ""),
   ("Interdisciplinary Graduate Program in Neuroscience", "NEURO", "https://neuroscience.grad.uiowa.edu/", "mixed", True, "keep psychology-relevant people")]),
 (100, "University of San Diego", []),
 (100, "University of South Florida", [
   ("Department of Psychology", "PSY", "https://www.usf.edu/arts-sciences/departments/psychology/", "main", True, "")]),
]

def slug(s):
    s = s.replace("–", "-").replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

out = []
for rank, name, units in U:
    out.append({
        "slug": slug(name), "university": name, "rank_usnews_national": rank,
        "no_phd_units": not any(u[4] for u in units),
        "units": [{"name": n, "field": t, "unit_url": url, "home": home, "include": inc,
                   "filter_psych": t == "NEURO" and home != "main",
                   "note": note} for n, t, url, home, inc, note in units],
    })
assert len(out) == 108, len(out)
# directory pages and renamed units found after the first scraper run (data/psych/fixes.json)
import os
fx = os.path.join(os.path.dirname(sys.argv[1]), "fixes.json")
if os.path.exists(fx):
    F = json.load(open(fx))
    for p in out:
        for u in p["units"]:
            u.update(F.get(p["slug"] + "|" + u["name"], {}))
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
print(len(out), "universities,", sum(len(p["units"]) for p in out), "units,",
      sum(u["include"] for p in out for u in p["units"]), "included")
